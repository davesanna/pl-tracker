from uuid import uuid4
from src.pl_tracker.database import SupabaseClient
from src.pl_tracker.gspread import GSpreadClient
import streamlit as st
import pandas as pd
import gspread
from dotenv import load_dotenv
import os

load_dotenv()

gspread_client = GSpreadClient()

supabase_client = SupabaseClient(
    os.environ["SUPABASE_URL"], os.environ["SUPABASE_API_KEY"]
).client


def get_available_programs(user_id):
    """Retrieve the list of available programs from the Google Spreadsheet."""

    programs_table = supabase_client.table("programs").select("*").execute().data

    available_programs = {
        entry["name"]: entry["id"]
        for entry in programs_table
        if entry["user_id"] == user_id
    }

    return available_programs


def get_spreadsheet_data(spreadsheet_name, worksheet_name):
    """Retrieve data from a specific worksheet in a Google Spreadsheet."""
    return gspread_client.get_df_from_worksheet(
        spreadsheet_name=spreadsheet_name, worksheet_name=worksheet_name
    )


def get_spreadsheet_worksheets(spreadsheet_name):
    """Retrieve the list of worksheets in a Google Spreadsheet."""
    spreadsheet = gspread_client.get_spreadsheet(spreadsheet_name)
    return [worksheet.title for worksheet in spreadsheet.worksheets()]


def sync_existing_programs():
    """Sync existing programs from the Google Spreadsheet to the Supabase database."""
    available_programs = get_available_programs("6dd48309-160b-4f8f-9354-270aa3808d76")

    composite_keys = [
        "Week",
        "Day",
        "Exercise",
        "Sets",
        "min_reps",
        "max_reps",
        "RPE Target",
        "program_id",
    ]

    for program, program_id in available_programs.items():
        print(f"Syncing program: {program} with ID: {program_id}")
        db_content = pd.DataFrame(
            supabase_client.table("sessions")
            .select("*")
            .eq("program_id", program_id)
            .execute()
            .data
        )
        worksheet = get_spreadsheet_data("PL Programs", program)

        if not worksheet.empty:
            cleaned_data = clean_worksheet(worksheet, program_id)

            df_merged = cleaned_data.merge(
                db_content, on=composite_keys, suffixes=("_new", "_db")
            )

            value_columns = [
                col for col in cleaned_data.columns if col not in composite_keys
            ]

            changed_mask = False
            for col in value_columns:
                changed_mask |= df_merged[f"{col}_new"] != df_merged[f"{col}_db"]

            changed = df_merged[changed_mask]

            if changed.empty:
                print(f"No changes found for {program}, skipping.")
                continue
            else:

                print(f"Found {len(changed)} changed records for {program}.")

                for _, row in changed.iterrows():
                    update_payload = {col: row[f"{col}_new"] for col in value_columns}
                    match_filter = {key: row[key] for key in composite_keys}

                    response = (
                        supabase_client.table("sessions")
                        .update(update_payload)
                        .match(match_filter)
                        .execute()
                    )

                print(response)
            print(f"Successfully synced {len(changed)} records for {program}.")


def clean_worksheet(worksheet_df, program_id):

    df_clean = worksheet_df[
        ~worksheet_df.apply(
            lambda row: row.astype(str).str.strip().eq("").all(), axis=1
        )
    ]
    df_clean.columns = df_clean.iloc[1]
    df_clean = df_clean[2:]

    def is_number(x):
        try:
            float(x)
            return True
        except:
            return False

    mask = df_clean.apply(lambda row: row.apply(is_number).any(), axis=1)
    df_filtered = df_clean[mask].copy()

    df_filtered = df_filtered.replace("-", 0.0)

    # Step 2: Convert each column to numeric, coercing errors to NaN
    df_filtered = convert_df_strings_to_floats(df_filtered)

    header_row = df_filtered.columns.tolist()
    df_filtered = df_filtered[
        ~df_filtered.apply(lambda row: row.tolist() == header_row, axis=1)
    ]

    df_filtered = df_filtered.reset_index(drop=True)

    df_filtered = df_filtered.rename(
        columns={
            "% Min": "perc_min",
            "% Max": "perc_max",
            "Carico Min (kg)": "carico_min",
            "Carico Max (kg)": "carico_max",
            "Min. Reps": "min_reps",
            "Max. Reps": "max_reps",
        }
    )

    df_filtered["Exercise"] = df_filtered["Exercise"].str.title()
    df_filtered["program_id"] = program_id
    df_filtered["Test"] = df_filtered["Test"].astype(bool)
    return df_filtered


def try_convert_to_float(val):
    if isinstance(val, str):
        val = val.replace(",", ".")
    try:
        return float(val)
    except (ValueError, TypeError):
        return val


def convert_df_strings_to_floats(df):
    return df.applymap(try_convert_to_float)


def sync_new_spreadsheets_to_database(spreadsheet_name="PL Programs"):
    """Sync data from a Google Spreadsheet to the Supabase database."""
    available_programs = get_available_programs("6dd48309-160b-4f8f-9354-270aa3808d76")

    worksheets = get_spreadsheet_worksheets(spreadsheet_name)

    for worksheet_name in worksheets:
        try:
            print(f"Processing {worksheet_name}...")
            if f"{worksheet_name}" in available_programs:
                print(
                    f"Program {worksheet_name} already exists in the database, skipping."
                )
                continue

            program_id = str(uuid4())
            worksheet = get_spreadsheet_data(spreadsheet_name, f"{worksheet_name}")
            if not worksheet.empty:
                cleaned_data = clean_worksheet(worksheet, program_id)
                cleaned_data["id"] = [str(uuid4()) for _ in range(len(cleaned_data))]

                supabase_client.table("sessions").insert(
                    cleaned_data.to_dict(orient="records")
                ).execute()

                supabase_client.table("programs").insert(
                    {
                        "id": program_id,
                        "name": f"{worksheet_name}",
                        "date": pd.Timestamp.now().isoformat(),
                        "user_id": "6dd48309-160b-4f8f-9354-270aa3808d76",
                    }
                ).execute()
                print(f"Successfully synced {worksheet_name}.")

        except gspread.exceptions.WorksheetNotFound as e:
            print(f"Worksheet {worksheet_name} not found, stopping.")
            break


if __name__ == "__main__":

    print("Starting sync process...")

    print("Syncing existing programs from Google Spreadsheet to Supabase...")

    sync_existing_programs()

    print("Sync existing programs completed.")

    print("Syncing new programs from Google Spreadsheet to Supabase...")

    sync_new_spreadsheets_to_database()

    print("Sync new programs completed.")
