from genson import SchemaBuilder
from dotenv import load_dotenv
import json, sys, os, io

generatedSchemas = {}
schemaSuffix="Data"

def readFiles(mdmsPath, schemaPath):
    for root, dirs, files in os.walk(mdmsPath):
        for file in files:
            if file.endswith(".json"):
                filePath = os.path.join(root, file)
                print("generating schema for {}".format(filePath))
                mdmsData = getFileData(filePath)
                if mdmsData != None:
                    try:
                        createJsonSchema(mdmsData, schemaPath)
                        print("Schema generated ".format(filePath))
                    except Exception as ex:
                        print("Schema feneration failed !")
                        print(ex)
                    

def getFileData(filePath): 
    try:
        f = open(filePath)
        data = json.load(f)
        if "tenantId" in data and "moduleName" in data:
            return data
        else:
            print("tenantId or moduleName is missing in the file: " + filePath)
            return None
    except Exception as ex:
        print(ex)
        print("JSON error in file - " + filePath)

def createJsonSchema(data, schemaPath):
    try:
        masterName = getFileName(data)
        if not generatedSchemas.get(masterName):
            builder = SchemaBuilder(schema_uri="http://json-schema.org/draft-07/schema")
            builder.add_object(data)
            schema = builder.to_schema()
            fileName = '{}/{}.json'.format(schemaPath, masterName)
            schema = changeJsonSchemaToSunbirdSchema(schema, masterName)
            try:    
                with io.open(fileName, 'w', encoding='utf-8') as f:
                    f.write(json.dumps(schema, indent = 4, ensure_ascii=False))
                    f.close()
                    generatedSchemas[masterName] = 1
            except Exception as ex:
                print("Exception on writing schema on file.")
                raise ex
    except Exception as ex:
        raise ex
    

def getFileName(data):
    masterName = None
    for key, value in data.items():
        if key != "tenantId" and key != "moduleName" and data[key] is not None:
            masterName = key
    return masterName

def changeJsonSchemaToSunbirdSchema(schema, masterName):
    try:
        schemaName = '{}{}'.format(masterName, schemaSuffix)
        newSchema = {}
        newSchema["$schema"] = "http://json-schema.org/draft-07/schema"
        newSchema["type"] = "object"

        newSchema["properties"] = {}
        newSchema["properties"][masterName] = {
            "$ref": "#/definitions/"+schemaName
        }
        newSchema["required"] = [masterName]
        newSchema["title"] = schemaName

        definations = {}
        del schema["$schema"]
        definations[schemaName] = schema
        newSchema["definitions"] = definations

        newSchema["_osConfig"] = {
            "osComment": [
                "This section contains the specific configuration information",
                "privateFields: Optional; list of field names to be encrypted and stored in database",
                "signedFields: Optional; list of field names that must be pre-signed",
                "indexFields: Optional; list of field names used for creating index. Enclose within braces to indicate it is a composite index. In this definition, (serialNum, schoolCode) is a composite index and schoolName is a single column index.",
                "uniqueIndexFields: Optional; list of field names used for creating unique index. Field names must be different from index field name",
                "systemFields: Optional; list of fields names used for system standard information like created, updated timestamps and userid"
            ],
            "systemFields": [
                "osCreatedAt",
                "osUpdatedAt"
            ]
        }
        return newSchema
    except Exception as ex:
        print("Exception while changing schema to sunbird schema.")
        print(ex)
        return None


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
        
    readFiles(path, schemaPath)
    


