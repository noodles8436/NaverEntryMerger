# ![Entry Logo](github/logo.png) NaverEntryMerger
Naver에서 제공하는 Entry Offline 파일들(.ent) 병합하는 Python 프로그램 입니다.  
  
**본 프로젝트는 연세대학교 미래캠퍼스 2022 동계 머레이 봉사단 SWeet 팀**에서  
Entry를 활용한 교육 프로그램에 사용하기 위하여 제작하였습니다.

## What is Entry-Offline ?

엔트리 오프라인은 [엔트리 웹 사이트](https://playentry.org/)에 접속할 수 없는 오프라인 환경에서도 엔트리를 사용할 수 있도록 제작된 프로그램입니다. 엔트리 오프라인은 [Electron](https://electronjs.org/) 기반으로 만들어졌으며,
[entryjs](https://github.com/entrylabs/entryjs) 와 [entry-hw](https://github.com/entrylabs/entry-hw) 프로젝트를 [bower](https://bower.io/) 를 통해 내장하고 있습니다.

## How To Use ?
해당 프로젝트를 다운 받아 EntryFile 폴더 내에 병합할 .ent 파일을 넣습니다.  
이후 EntryMerger.py 파일을 python으로 실행하면, 각 파일 내의 모든 변수 및 장면들이  
하나의 .ent 파일로 병합되어 result.ent 파일로 저장됩니다.
  
```
python EntryMerger.py
```

## Requirements
파이썬 내장 라이브러리만을 사용하였기 때문에 Python 만 설치되어 있으면 가능합니다! 

## Contact
연세대학교 미래캠퍼스 소프트웨어학부 김태욱 학부생  
Email : xodnr8436@yonsei.ac.kr
