from genson import SchemaBuilder
from dotenv import load_dotenv
import json, sys, os, io

schemaSuffix="Data"

if __name__ == "__main__":
    load_dotenv()
    path = None
    mdmsPath = os.getenv('MDMS_DATA_PATH')
    mdmsSuffix = os.getenv('SCHEMA_SUFFIX')
    if mdmsPath is not None:
        schemaSuffix = mdmsSuffix
    if len(sys.argv) > 1:
        path = sys.argv[1]
    elif mdmsPath != None:
        path = mdmsPath
    else:
        print("Please provide mdms path")
        sys.exit()

    schemaPath = os.getenv('SCHEMA_PATH')
    schemaPathExist = os.path.exists(schemaPath)
    if not schemaPathExist:
        print("Please provide schema output path")
        sys.exit()