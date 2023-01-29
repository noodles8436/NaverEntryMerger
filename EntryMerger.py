import tarfile
import os
import json
import random
import string
import numpy as np
import shutil

ENT_FILES_FOLDER    =   "./EntryFiles"  # 병합할 .ent 파일이 존재하는 폴더 위치입니다.
MERGE_TEMP_FOLDER   =   "./MergeTemps"  # 병합 과정에서 임시로 사용될 폴더 위치입니다.
RANDOM_STRING_POOL  =   string.ascii_lowercase + string.digits # 병렬 과정에서 랜덤으로 id 값을 생성하는 함수에 사용되는 변수입니다.


def make_tarfile(output_filename, source_dir):
    """
    source_dir 폴더를 기준으로 tar.gz 파일을 압축하는 함수입니다.
    :param output_filename: 출력 결과물 이름입니다.
    :param source_dir: 압축을 시행할 폴더의 위치입니다.
    :return: None
    """
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def getRandom_Letter(size: int) -> str:
    """
    랜덤 String 값을 size 크기만큼 생성하는 함수입니다.
    :param size: 생성할 랜덤 String의 크기
    :return: str
    """

    # 생성된 랜덤 String 값을 저장할 변수를 선언합니다.
    result = ""

    # 전달 받은 size 만큼 랜덤 String 을 생성합니다.
    for i in range(size):
        result += random.choice(RANDOM_STRING_POOL)

    # Size 길이를 가지는 랜덤 String 값을 반환합니다.
    return result


class EntryFile:
    """
    Entry ( .ent 확장자 ) 파일에 대해서 데이터 가공 및 관리를 담당하는 클래스입니다.
    """

    def __init__(self, path: str):
        """
        Entry File Class 의 생성자 함수 입니다.
        입력 받은 path ( .ent 파일의 경로 ) 에 대해서 압축을 풀고 json 파일을 읽어옵니다.
        :param path: .ent 파일의 경로
        """

        # 확장자가 .ent가 아닌경우 Exception을 발생합니다.
        if path.split(".")[-1] != "ent":
            raise Exception(f"PATH = {path}, 파일 확장자가 .ent가 아닙니다!")

        # 이미 압축 해제된 동일한 이름의 폴더가 있는 경우 삭제하고 진행합니다.
        if os.path.isdir(path[:-4]):
            shutil.rmtree(path[:-4])

        # .ent 파일을 tar 형식으로 압축 해제합니다.
        tar_gz_file = tarfile.open(path, mode='r:gz')
        tar_gz_file.extractall(path[:-4])
        tar_gz_file.close()

        self.path = path

        # 압축이 해제된 프로젝트 폴더 경로를 선언합니다.
        self.project_dir = os.path.join(path[:-4], 'temp')

        # 해당 프로젝트 폴더 내에 핵심 파일인 project.json 파일의 경로를 선언합니다.
        project_json_dir = os.path.join(self.project_dir, 'project.json')

        # project.json 파일을 열고 json을 통해서 dict 형태로 변환합니다.
        _file = open(project_json_dir, 'r', encoding='utf-8')
        self.data: dict = json.load(_file)

        # project.json의 str 형태와 object 및 item 들의 고유 id list를 추출하여 저장합니다.
        # 이는 추후 타 파일과 병합시, id 중복으로 인한 충돌을 방지하기 위함입니다.
        self.data_string: str = json.dumps(self.data)
        self.id_list = self.getObjectIDs()

        # 더불어 .ent 파일 내에 존재하는 folder 이름들을 변수로 생성하여 저장합니다.
        # 이는 추후 타 파일과 병합시, folder 이름 중복으로 인한 충돌을 방지하기 위함입니다.
        self.dataFolder_list = self.getDataFolders()

        # project.json 파일을 json을 통해서 dict 형태로 변환한 후, 파일 Descriptor를 닫습니다.
        _file.close()

    def getObjectIDs(self) -> list:
        """
        해당 함수는 .ent 파일을 tar.gz 형식으로 압축을 해제한 후 생긴 temp 폴더 내에
        project.json 파일 내의 id 값들만을 추출하여 list 형태로 반환하는 함수입니다.

        :return: list
        """
        # project.json 파일 내에 존재하는 id 값들을 추출한 후 저장할 list 변수를 선언합니다.
        _id_list = []

        # json 을 string 형태로 저장된 self.data_string 변수에서 [ ] { } " ' 을 삭제하고
        # , 를 : 로 변환하고, 띄어쓰기를 제거하여 : 를 기준으로 split을 진행합니다.
        _string = self.data_string.replace("[", "").replace("{", "") \
            .replace("]", "").replace("}", "").replace("\"", "").replace("\'", "") \
            .replace(",", ":").replace(" ", "")
        _stringSplit = _string.split(":")

        # ... id:aaaa ... 라고 된 string 은 id, aaaa로 split 되어 배열에 저장되어 있으니
        # 만약 id 라는 string 값을 가지는 원소가 있으면, 그 다음 값은 id 의 값을 의미하므로, 이를 통해 id 값을 추출합니다.
        for i in range(len(_stringSplit)):
            if _stringSplit[i] == "id":
                _id_list.append(str(_stringSplit[i + 1]))

        # 중복되는 id 값들을 np.unique 함수를 통해서 정리합니다.
        result = np.unique(_id_list)

        # 정리된 id 값들이 담긴 numpy 변수 result 를 list 형으로 변환하여 반환합니다.
        result = result.tolist()
        return result

    def getDataFolders(self) -> list:
        """
        .ent 파일을 압축 해제 한 후, temp 폴더 내에 존재하는 폴더들의 이름들을 전부 추출하여
        list 타입으로 반환하는 함수입니다.

        :return: list
        """

        # .ent 파일을 압축 해제 한 후, temp 파일에 대한 전체 경로가 담긴 self.project_dir을 활용하여
        # temp 폴더 내의 모든 file 이름들을 folders 변수에 저장합니다.
        folders = os.listdir(self.project_dir)

        # temp 폴더 내의 모든 폴더 이름들을 저장하기 위한 list 변수를 선언합니다.
        result = []

        # temp 폴더 내의 project.json 파일과 같이 폴더가 아닌 것들을 제외하고, 나머지 폴더들을
        # 전체 경로로 변환하여 result 변수 내에 저장합니다.
        for _folder in folders:
            if os.path.isdir(os.path.join(self.project_dir, _folder)):
                result.append(_folder)

        # temp 폴더 내의 모든 폴더들에 대한 전체 경로가 담긴 list 변수를 반환합니다.
        return result

    def changeDataFolderName(self, folder: str, new_folder: str) -> None:
        """
        folder 명이 겹쳤을 때, temp 폴더 내에 존재하는 폴더 이름을 변경하는 함수입니다.
        :param folder: 이름을 변경할 folder 명입니다.
        :param new_folder: 새롭게 명명할 folder 의 이름입니다.

        :return: None
        """

        # 폴더 명을 정정합니다.
        os.rename(os.path.join(self.project_dir, folder),
                  os.path.join(self.project_dir, new_folder))

        # EntryFile 객체 내에 저장된, temp 폴더 내에 존재하는 folder 이름 명들을 저장하는 self.dataFolder_list 변수와
        # project.json 파일 내에 저장되어있는, 겹친 폴더 이름을 새로운 폴더 이름으로 변경합니다.
        # changeObjectId 는 폴더, 오브젝트에 부여된 id 값 관계없이, 특정 id를 변경하는 함수입니다.
        self.dataFolder_list = self.getDataFolders()
        self.changeId(f"\\{folder}\\", f"\\{new_folder}\\")

    def isIDExist(self, id: str) -> bool:
        """
        파라미터로 받은 object_id가 이미 project.json 파일 내에 존재하는 id 값인지 반환합니다.
        self.id_list 변수는 .ent 파일 내 project.json 파일 안에서 존재하는 id 값들을 저장하는 list 변수입니다.
        :param id: 검색할 id 값입니다.

        :return: bool
        """
        return id in self.id_list

    def changeId(self, object_id: str, new_id: str) -> None:
        """
        .ent 파일을 압축 해제 한 후, project.json 파일 내에 존재하는 object_id 값을 new_id 값으로 변경합니다.
        :param object_id: 변경하고자 하는 id 값
        :param new_id: 새로운 id 값

        :return: None
        """

        # project.json 파일을 string 형식으로 저장하는 self.data_string 변수에서 id 값을 변경합니다
        self.data_string = self.data_string.replace(object_id, new_id)

        # 변경된 json 값을 string 형식으로 가지는 self.data_string 변수를
        self.data = json.loads(self.data_string)
        self.id_list = self.getObjectIDs()

    def getScene(self) -> list[dict]:
        """
        .ent 파일 내의 project.json 안에 저장된 scenes (장면들이 저장된 list[dict]) 를 반환합니다.
        :return: list[dict]
        """
        return self.data["scenes"]

    def getObjects(self) -> list[dict]:
        """
        .ent 파일 내의 project.json 안에 저장된 Objects (장면들이 저장된 list[dict]) 를 반환합니다.
        :return: list[dict]
        """
        return self.data["objects"]

    def getVariables(self) -> list[dict]:
        """
        .ent 파일 내의 project.json 안에 저장된 Variables (장면들이 저장된 list[dict]) 를 반환합니다.
        :return:
        """
        return self.data["variables"]

    def getFunctions(self) -> list[dict]:
        """
        .ent 파일 내의 project.json 안에 저장된 Functions (장면들이 저장된 list[dict]) 를 반환합니다.
        :return: list[dict]
        """
        return self.data["functions"]

    def getMessages(self) -> list[dict]:
        """
        .ent 파일 내의 project.json 안에 저장된 Messages (장면들이 저장된 list[dict]) 를 반환합니다.
        :return: list[dict]
        """
        return self.data["messages"]

    def getInterface(self) -> dict:
        """
        .ent 파일 내의 project.json 안에 저장된 Interface (장면들이 저장된 dict) 를 반환합니다.
        :return: dict
        """
        return self.data["interface"]

    def mergeVariable(self, object_name: str) -> None:
        """
        같은 이름을 가지는 중복된 전역 변수들을 하나로 통합하는 함수입니다.
        가령 "실패한 횟수" 라는 이름의 중복된 변수들을 하나로 통합하여 장면 관계없이
        실패한 횟수를 체크하도록 변수를 통일합니다.

        :param object_name: 통일할 변수의 이름
        :return: None
        """

        # List[Dict] 형태로 저장된 변수들을 variables 변수에 저장합니다.
        variables = self.getVariables()

        # 하나로 통일할 변수의 id 값을 저장할 변수를 선언합니다.
        fix_id = None
        for var in variables:
            # 변수가 object_name 이름을 가질 경우
            if object_name == var["name"]:
                # 기준으로 할 id 값이 정해지지 않았다면
                if fix_id is None:
                    # 해당 변수의 id 값만 남겨둡니다.
                    # 후우 fix_id 의 값을 사용해서 다른 중복된 변수들의 id 들을 치환하여 삭제합니다.
                    fix_id = var["id"]
                else:
                    # fix_id 값이 아닌 중복된 변수의 id 값을 삭제합니다.
                    self.removeVariable(var["id"])
                    # 다른 오브젝트에서 중복된 변수의 id 값을 사용한다면 fix_id로 변경하여
                    # fix_id 를 가지는 변수만을 사용하도록 통일합니다.
                    self.changeId(var["id"], fix_id)

    def removeVariable(self, id: str) -> None:
        """
        .ent 파일 내 project.json 파일 내에 정의된 전역 변수들 중
        함수에 전달 받은 id 값을 가지는 변수를 삭제합니다. ( 단 사용하지 않는 전역 변수 id 만을 전달해야합니다. )
        사용중인 중복된 전역변수를 하나로 통합하려면 mergeVariables 함수를 사용하세요.

        :param id: 삭제할 변수 id 값
        :return: None
        """

        # 삭제할 변수를 제외한 나머지 변수 정보들을 저장할 removed_variables_list 변수를 선언합니다.
        removed_variable_list = []

        # 현제 .ent 파일 안에 저장된 엔트리 전역 변수들의 정보를 가져옵니다.
        variables = self.getVariables()

        # id 값을 가지는 변수 정보를 제외한 나머지 변수 정보들을 removed_variables_list에 저장합니다.
        for var in variables:
            if var["id"] != id:
                removed_variable_list.append(var)

        # 제거할 변수를 제외한 나머지 변수 정보들이 담긴 removed_variables_list 변수를 기반으로
        # EntryFile 객체 내의 정보들을 새로고침합니다.
        self.data["variables"] = removed_variable_list
        self.data_string = json.dumps(self.data)

    def makeENTFile(self) -> None:
        """
        현재 EntryFile 객체를 기반으로 새로운 .ent 파일을 생성합니다.
        :return: None
        """

        # 현재 .ent 압축을 해제한 폴더 내에 project.json 파일을
        # EntryFile 객체에 저장된 self.data로 변경하여 Json 파일을 저장합니다.
        with open(os.path.join(self.project_dir, "project.json"), 'w', encoding='utf-8') as file:
            json.dump(self.data, file)

        # 이미 존재하는 기존의 .ent 파일을 삭제합니다.
        if os.path.exists(self.path):
            os.remove(self.path)

        # 새로운 .ent 파일을 생성합니다.
        # MergeTemps/temp 폴더를 tar.gz 파일로 압축한 후, 확장명을 .ent 으로 설정합니다.
        make_tarfile("./result.ent", self.project_dir)


class EntryMerger:
    """
    Entry ( .ent 확장자 ) 들을 EntryFile Class 화하고, 각 EntryFile 객체들을 정리한 뒤
    하나의 Entry ( .ent 확장자 ) 로 변환하는 클래스입니다.
    """

    def __init__(self):
        """
        EntryMerger의 생성자 함수입니다.
        해당 함수는 .ent 파일의 .json 구조를 그대로 가지는 dict() 객체를 생성하여 저장합니다.
        aiUtilizeBlocks, expansionBlocks.. 등의 key 값은 전부 .ent 파일 내의 .json 파일 key값 구조를
        그대로 사용한 것입니다.
        """
        # 모든 .ent 파일의 .json 정보를 담기 위한 dict() 변수를 생성합니다.
        self.result_json = dict()

        # 아래의 key값들의 정의들은 EntryFiles 폴더 내의 .ent 파일과 관련 없이 고정적인 key값들입니다.
        self.result_json["aiUtilizeBlocks"] = []
        self.result_json["expansionBlocks"] = []
        self.result_json["externalModules"] = []
        self.result_json["externalModulesLite"] = []
        self.result_json["hardwareLiteBlocks"] = []
        self.result_json["isPracticalCourse"] = False
        self.result_json["name"] = "MergerResult"
        self.result_json["speed"] = 60
        self.result_json["tables"] = []

        # 아래의 key값들의 정의들은 EntryFiles 폴더 내의 .ent 파일안에서 .json 값들을 전부 저장하기 위해 선언된 key값들입니다.
        self.result_json["interface"] = dict()
        self.result_json["functions"] = []
        self.result_json["messages"] = []
        self.result_json["objects"] = []
        self.result_json["scenes"] = []
        self.result_json["variables"] = []

    def mergeJSON(self, entFile: EntryFile) -> None:
        """
        mergeJSON 함수는 EntryFile 객체의 entFile 파라미터를 받아서
        EntryMerger 객체안에 모든 .ent 파일들의 .json 정보들을 저장하는 self.result_json 변수 안에 저장합니다
        :param entFile: 합병할 .ent 파일의 EntryFile 객체
        :return: None
        """

        # .ent 파일 내에 .json 안에서 functions, messages, objects, scenes, variables key에 대해서만 추출하여
        # EntryMerger 객체안의 self.result_json dict 변수에 저장합니다.
        self.result_json["functions"] += entFile.getFunctions()
        self.result_json["messages"] += entFile.getMessages()
        self.result_json["objects"] += entFile.getObjects()
        self.result_json["scenes"] += entFile.getScene()
        self.result_json["variables"] += entFile.getVariables()

    def setInterface(self, entFile: EntryFile):
        """
        Interface는 .ent 파일을 실행하였을 때, 화면에 잡는 오브젝트 정보 및 화면에 띄워지는 정보를 저장하는 key값입니다.
        하나의 .ent 파일이 가지는 interface 값을 EntryMerger의 interface 값으로 저장합니다.

        :param entFile: 합병시 기준이 되는 .ent 파일의 EntryFile 객체입니다.
        :return: None
        """
        self.result_json["interface"] = entFile.getInterface()

    def getAllFilesPath(self) -> list:
        """
        file_path ( 합병할 .ent 파일이 모인 폴더 ) 내의 모든 .ent 파일에 대한
        절대 경로들을 list 형식으로 반환합니다.

        :return: list
        """
        # file_path 폴더 내에 모든 파일 이름을 추출합니다.
        filenames = os.listdir(ENT_FILES_FOLDER)

        # 파일의 전체 경로들을 저장할 list를 선언합니다.
        file_list = []

        # 각 파일 이름 앞에 폴더 경로를 결합하여 전체경로를 추출하고
        # 이를 file_list에 저장합니다
        for file in filenames:
            path = os.path.join(ENT_FILES_FOLDER, file)
            file_list.append(path)

        # 추출된 file_path 폴더 속 모든 파일에 대한 각각의 전체경로들을 list 형태로 반환합니다.
        return file_list

    def MergeAllEnt(self):
        """
        EntryFiles 폴더 내에 있는 모든 .ent 파일에 대해서 tar.gz 압축을 해제 한 후,
        내부의 Image 폴더들을 복사하여 MergeTemps 폴더에 옮깁니다.
        또한 .ent 파일 간 Image 폴더 이름이 겹치지 않도록, project.json 파일 내의 id 값이 겹치지 않도록 조정합니다.
        이후 MergeTemps 내의 폴더를 tar.gz 압축을 진행한 후 확장명을 .ent로 변경하여
        EntryFiles 폴더 내에 모든 .ent 파일이 병합된 하나의 result.ent 파일을 저장하고 종료합니다

        :return: None
        """
        # self.getAllFilesPath() 함수를 사용하여 EntryFiles 내에 존재하는 .ent 파일들의
        # 전체 경로가 담긴 list 변수를 저장합니다.
        EntryFilePaths: list = self.getAllFilesPath()

        # 추후 하나의 .ent 파일로 병합시에 사용되는 MergeTemps 폴더가 이미 존재하면
        # MergeTemps 폴더를 삭제하도록 합니다.
        if os.path.exists(MERGE_TEMP_FOLDER):
            shutil.rmtree(MERGE_TEMP_FOLDER)

        # MergeTemps 폴더를 만들고, MergeTemps 폴더 내에 temp 폴더를 생성합니다.
        # .ent 파일은 tar.gz 방식으로 압축을 해제하면 temp 폴더가 있기 때문에, 그 형식을 유지하기 위해
        # MergeTemps/temp 폴더를 생성합니다.
        os.mkdir(MERGE_TEMP_FOLDER)
        os.mkdir(os.path.join(MERGE_TEMP_FOLDER, "temp"))

        # EntryFiles 폴더 내에 모든 .ent 파일의 절대경로가 담긴 EntryFilePaths라는 List 변수에서
        # 가장 첫번째 .ent File에 대한 절대 경로를 가져옵니다.
        file = EntryFilePaths[0]

        # 해당 첫번째 .ent 파일에 대해서 EntryFile 객체를 생성합니다.
        entFile = EntryFile(file)

        # 첫번째 .ent 파일을 기준으로 다른 .ent 파일을 붙이기 위해서
        # 첫번째 .ent 파일의 정보들을 EntryMerge 객체의 self.result_json dict 변수에 저장하고
        self.mergeJSON(entFile=entFile)

        # 첫번째 .ent 파일의 interface 값을 합병된 .ent 파일과 동일하게 설정합니다.
        self.setInterface(entFile=entFile)

        # 첫번째 .ent 파일의 절대경로가 담긴 .ent 파일이 압축 해제된 폴더 내의 temp 폴더까지의 경로를 저장합니다.
        # 이는 첫번째 .ent 파일이 가지는 정보들이 담긴 root Folder 경로입니다.
        # ex) firstFile.ent 압축 해제 -> EntryFiles/firstFile/temp
        dataFolders = os.listdir(os.path.join(file[:-4], "temp"))

        # 첫번째 .ent 파일이 압축해제된 폴더 내에 존재하는 폴더들(이미지 정보가 담긴)을
        # MergeTemps/temp 폴더 내로 전부 옮깁니다.
        # 첫번째 .ent 파일의 폴더를 가져오는 것이므로, 폴더 명이 겹치는가? 를 검사할 필요없이
        # 그대로 복사해오면 됩니다.
        for folder in dataFolders:
            total_folder = os.path.join(file[:-4], "temp", folder)
            # .ent 파일 압축 해제 후 생긴 폴더 내에 존재하는 project.json 파일을 제외한 모든 폴더에 대해서만
            # MergeTemps/temp 폴더로 복사하는 과정을 수행합니다.
            if os.path.isdir(total_folder) is False:
                continue
            target_folder = os.path.join(MERGE_TEMP_FOLDER, "temp", folder)
            shutil.copytree(total_folder, target_folder)

        # 첫번째 .ent 파일에 대한 project.json 파일을 저장하였고, 폴더 또한 MergeTemps/temp 폴더로 옮겼습니다.
        # 이후 다른 .ent 파일을 합병할 때 폴더 명이 겹치는지, project.json 내의 id 값들이 겹치는지 확인하기 위해서
        # 현재까지 저장된 폴더 이름들과 id 들을 저장하는 변수 object_ids, datafolder_list 변수를 선언하니다.
        # 이후 두 변수에 첫번째 .ent 파일에 대한 폴더 이름들과 id 값들을 저장합니다.
        object_ids = entFile.getObjectIDs()
        datafolder_list = entFile.getDataFolders()

        # 첫번째 파일을 성공적으로 합병하였으므로, EntryFilePaths에서 첫번째 .ent 파일에 대한 절대경로를 제거합니다.
        EntryFilePaths = EntryFilePaths[1:]

        # EntryFilesPaths에 남은 나머지 파일들에 대해서 Merge를 진행합니다.
        for file in EntryFilePaths:
            # .ent 파일을 EntryFile 객체로 불러옵니다.
            entFile = EntryFile(file)

            # .ent 파일 내의 project.json 파일에 들어있는 id 값들과 현재까지 저장된 id 값들 사이 겹치는
            # id 들을 추출하여 duplicated_ids list 변수에 저장합니다.
            duplicated_ids = list(set(object_ids).intersection(entFile.getObjectIDs()))
            for dup_id in duplicated_ids:
                # 겹치는 id를 변경하기 위하여, 새로운 id 값을 생성한 후 저장하기 위한 new_id 변수를 생성합니다.
                new_id = ""
                while True:
                    # 반복을 통해서 4자리 Random id를 생성하고, 생성된 id가 이미 존재하는 id 들과
                    # 다시 겹치는지 확인합니다. 이때, 새로 생성된 id 값은 이미 병합된 ent 파일의 id 값들과도 겹쳐서는 안되며
                    # 지금 현재 병합을 시도하고 있는 ent 파일 내의 id 값들과도 겹쳐서는 안됩니다.
                    new_id = getRandom_Letter(size=4)
                    if new_id in object_ids or new_id in entFile.getObjectIDs():
                        continue
                    break

                # 생성된 새로운 id 값을 사용하여 겹치는 이름을 변경합니다.
                entFile.changeId(dup_id, new_id)

            # .ent 파일 내에 존재하는 folder 들의 이름들과 이미 병합된 folder 들 사이 겹치는 이름들을 추출하여
            # duplicated_folders list 변수 내에 저장합니다.
            duplicated_folders = list(set(datafolder_list).intersection(entFile.getDataFolders()))
            for dup_folder in duplicated_folders:
                # 겹치는 folder 이름을 변경하기 위하여, 새로운 folder 이름을 생성한 후 저장하기 위한 new_id 변수를 생성합니다.
                new_id = ""
                while True:
                    # 반복을 통해서 2자리 Random id를 생성하고, 생성된 folder들의 이름이 이미 존재하는 folder들의 이름들과
                    # 다시 겹치는지 확인합니다. 이때, 새로 생성된 folder 이름은 이미 병합된 ent 파일의 folder들의 값들과도
                    # 겹쳐서는 안되며 지금 현재 병합을 시도하고 있는 ent 파일 내의 folder 이름들과도 겹쳐서는 안됩니다.
                    new_id = getRandom_Letter(size=4)
                    if new_id in datafolder_list or new_id in entFile.getDataFolders():
                        continue
                    break

                # 생성된 새로운 folder 이름을 사용하여 겹치는 folder 이름을 변경합니다.
                entFile.changeDataFolderName(dup_folder, new_id)

            # 파일을 병합하고, 현재까지 축적된 objects id 와 datafolder list를 저장합니다.
            self.mergeJSON(entFile=entFile)
            object_ids += entFile.getObjectIDs()
            datafolder_list += entFile.getDataFolders()

            # 이미 생성된 .ent 파일 내의 폴더들과 이름이 겹치지 않는 폴더 이름들로 변경해두었으니,
            # 모든 폴더들을 MergeTemps/temp 폴더 내에 복사합니다.
            # 이를 위해서 이름들이 수정된 폴더들의 전체 경로들을 저장하는 dataFolders 변수를 생성합니다.
            dataFolders = os.listdir(os.path.join(file[:-4], "temp"))

            # 모든 폴더들을 MergeTemps/temp 폴더 내로 복사합니다.
            for folder in dataFolders:
                total_folder = os.path.join(file[:-4], "temp", folder)
                if os.path.isdir(total_folder) is False:
                    continue
                target_folder = os.path.join("./MergeTemps", "temp", folder)
                shutil.copytree(total_folder, target_folder)

        # 모든 .ent 파일 내에 .json 파일들 에 담긴 정보들은 EntryMerge 객체 내의 self.result_json에 저장하였고
        # 모든 .ent 파일 내에 Image가 담긴 폴더들을 MergeTemps/temp 폴더 내로 복사하였으니,
        # MergeTemps/temp 폴더 내에 project.json 파일을 EntryMerge 객체 내의 self.result_json 변수를 사용하여 생성합니다.
        file_path = "./MergeTemps/temp/project.json"
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(self.result_json, file)

        # MergeTemps/temp 폴더를 tar.gz 파일로 압축한 후, 확장명을 .ent 으로 설정합니다.
        make_tarfile("./result.ent", "./MergeTemps/temp")


if __name__ == "__main__":
    entMerge = EntryMerger()
    entMerge.MergeAllEnt()

    entFile = EntryFile("./result.ent")
    entFile.mergeVariable("실패한 횟수")
    entFile.makeENTFile()
