import pandas as pd
from src.pl_tracker.models import SessionMetadata
from supabase import create_client
from uuid import uuid4
from datetime import datetime
import streamlit as st


class SupabaseClient:
    def __init__(self, url: str, api_key: str):
        self.client = create_client(url, api_key)

    def upload_nutrition_data(self, nutrition_data: pd.DataFrame, user_id: str):
        """
        Upload nutrition data to the database.

        Args:
            nutrition_data (dict): Nutrition data to upload.
            user_id (str): The user ID to associate with the nutrition data.

        Returns:
            None
        """
        keys = ["id", "user_id", "Date"]
        columns_to_check = [col for col in nutrition_data.columns if col not in keys]

        db_nutrition_data = self.fetch_nutrition_data(user_id)

        nutrition_data["user_id"] = st.session_state["selected_user_id"]
        nutrition_data["Date"] = pd.to_datetime(nutrition_data["Date"]).dt.date
        nutrition_data[columns_to_check] = nutrition_data[columns_to_check].fillna(0)

        merged_data = pd.merge(
            db_nutrition_data,
            nutrition_data,
            on=["Date", "user_id"],
            how="outer",
            suffixes=("_old", ""),
        )

        changed_mask = False
        for col in columns_to_check:
            changed_mask |= merged_data[f"{col}_old"] != merged_data[f"{col}"]

        changed = merged_data[changed_mask]

        changed.loc[changed["id"].isna(), "id"] = changed.loc[
            changed["id"].isna(), "id"
        ].apply(lambda _: str(uuid4()))

        if not changed.empty:
            st.warning(
                "There are changes in your nutrition data. Please review before uploading."
            )

            to_upload = changed[keys + columns_to_check].copy()
            to_upload["Date"] = to_upload["Date"].astype(str)

            st.dataframe(to_upload)

            if st.button("Yes I'm ready to rumble"):
                response = (
                    self.client.table("nutrition")
                    .upsert(to_upload.to_dict("records"))
                    .execute()
                )

                if response:
                    return True
        else:
            st.info("No changes detected in your nutrition data.")

    def fetch_nutrition_data(self, user_id: str):
        """Fetch nutrition data from the database."""
        nutrition_data = pd.DataFrame(
            self.client.table("nutrition")
            .select("*")
            .in_("user_id", user_id)
            .execute()
            .data
        )

        nutrition_data["Date"] = pd.to_datetime(nutrition_data["Date"]).dt.date
        return nutrition_data

    def get_bucket_content(self, bucket: str, user_id: str = None):
        id_programs = self.client.storage.from_(bucket).list(
            f"{user_id}/",
            {
                "sortBy": {"column": "created_at", "order": "asc"},
            },
        )
        response = [
            item["name"] for item in id_programs if item["name"].endswith(".pdf")
        ]
        return response

    def get_bucket_signed_url(self, bucket: str, file_path: str):
        """Get a signed URL for a file in the specified bucket."""
        return self.client.storage.from_(bucket).create_signed_url(
            st.session_state["selected_user_id"] + "/" + file_path, 60 * 60
        )["signedURL"]

    def upload_program_file(self, file, user_id: str):
        """
        Upload a program file to the specified bucket.

        Args:
            file (file): The file to upload.
            user_id (str): The user ID to associate with the program file.

        Returns:
            None
        """
        remote_path = f"{user_id}/{file.name}"
        file_content = file.getvalue()
        self.client.storage.from_("programs").upload(remote_path, file_content)
        st.success("📄 Program file uploaded!")

    def get_user_video(self, user_id: str, path: str):
        """
        Fetch video metadata for a specific user.

        Args:
            user_id (str): The user ID to fetch videos for.

        Returns:
            pd.DataFrame: DataFrame containing video metadata.
        """
        video_url = self.client.storage.from_("videos").create_signed_url(
            user_id + "/" + path, 60 * 60
        )["signedURL"]

        return video_url

    def update_video_meta(self, video_id: str, meta: SessionMetadata):
        """
        Update video metadata in the database.

        Args:
            video_id (str): The ID of the video to update.
            meta (SessionMetadata): The metadata to update.

        Returns:
            None
        """
        self.client.table("videos").update(meta.dict()).eq("id", video_id).execute()
        st.success("📹 Video metadata updated!")

    def upload_video_and_meta(self, user_id, file, meta: SessionMetadata):
        video_id = str(uuid4())
        remote_path = f"{user_id}/{meta["program"]}/Week {meta["week"]}/Day {meta["day"]}/{meta["exercise"]}/{meta["video_name"]}"

        file_content = file.getvalue()
        self.client.storage.from_("videos").upload(remote_path, file_content)
        # url = self.client.storage.from_("videos").get_public_url(remote_path)[
        #     "publicURL"
        # ]
        # insert into videos
        self.client.table("videos").insert(
            {
                "id": video_id,
                "user_id": user_id,
                # "url": url,
                **meta,
            }
        ).execute()

        st.dataframe(st.session_state["videos_data"])

        st.session_state["videos_data"] = pd.concat(
            [
                st.session_state["videos_data"],
                pd.DataFrame(
                    [
                        {
                            "id": video_id,
                            "user_id": user_id,
                            "video_name": meta["video_name"],
                            "program": meta["program"],
                            "week": meta["week"],
                            "day": meta["day"],
                            "exercise": meta["exercise"],
                            "Sets": meta["Sets"],
                            "Reps": meta["Reps"],
                            "Effective Set": meta["Effective Set"],
                            "Weight": meta["Weight"],
                            "notes": meta["notes"],
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
        st.success("📹 Video uploaded!")
