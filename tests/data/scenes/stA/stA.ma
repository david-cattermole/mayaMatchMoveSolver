//Maya ASCII 2018ff09 scene
//Name: stA.ma
//Last modified: Wed, Jan 30, 2019 04:42:53 AM
//Codeset: 949
requires maya "2018ff09";
requires -nodeType "mmMarkerScale" -nodeType "mmMarkerGroupTransform" "mmSolver" "1.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2018";
fileInfo "version" "2018";
fileInfo "cutIdentifier" "201811122215-49253d42f6";
fileInfo "osv" "Microsoft Windows 7 Business Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";
createNode transform -s -n "persp";
	rename -uid "507E6547-44E9-EBC9-736E-14825ACCB37F";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -36.691904944166197 20.201462300410867 221.63783073686304 ;
	setAttr ".r" -type "double3" -5.138352729602655 -9.3999999999997748 -5.0372561513311139e-17 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "3D87FA7A-4ABB-1DF3-4A82-A1BE13CB30D2";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 225.56090747567265;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "54E07D5A-4CD2-A7CD-C6D9-63A87580A149";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "6DAD267B-4F7A-FD37-241B-53B0F99D8136";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
createNode transform -s -n "front";
	rename -uid "11EC2F96-4E20-D457-7DB1-EBB1CE1E7B1F";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "E977DB45-4878-CED7-7961-1698E9EC398D";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
createNode transform -s -n "side";
	rename -uid "5F6ED8D5-4924-4E82-8348-4396CE875CA1";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "7DC83DA1-4817-A265-4C6E-059A82F7EFFF";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "Scene";
	rename -uid "0135AFEF-4904-1D6B-6319-DE81247E4648";
	setAttr ".ro" 2;
createNode transform -n "stA_1_1" -p "Scene";
	rename -uid "18B48172-4B9E-34B1-3F6E-D4B07B6AF6BB";
	setAttr ".ro" 2;
createNode camera -n "stA_1_1Shape1" -p "stA_1_1";
	rename -uid "1B31B2BD-46E1-49A0-36E2-65B4AF17490B";
	setAttr -k off ".v";
	setAttr ".rnd" no;
	setAttr ".cap" -type "double2" 0.87582530444564 0.58267716535433101 ;
	setAttr ".ff" 3;
	setAttr ".ncp" 0.01;
	setAttr ".sa" 180;
	setAttr ".imn" -type "string" "stA_1_1";
	setAttr ".den" -type "string" "stA_1_1_depth";
	setAttr ".man" -type "string" "stA_1_1_mask";
createNode transform -n "imagePlane1" -p "stA_1_1Shape1";
	rename -uid "5B915662-489F-B7D9-DA7D-17AF2FDBD8FA";
createNode imagePlane -n "imagePlaneShape1" -p "imagePlane1";
	rename -uid "D3A6956D-4033-1E8D-F880-7BB972C8A84C";
	setAttr -k off ".v";
	setAttr ".fc" 50;
	setAttr ".imn" -type "string" "e:/tuto/3de/stA/stA.0000.jpg";
	setAttr ".ufe" yes;
	setAttr ".cov" -type "short2" 1936 1288 ;
	setAttr ".f" 4;
	setAttr ".dic" yes;
	setAttr ".d" 4500;
	setAttr ".s" -type "double2" 0.87582530444564 0.58267716535433101 ;
	setAttr ".w" 10;
	setAttr ".h" 10;
	setAttr ".cs" -type "string" "sRGB";
createNode mmMarkerGroupTransform -n "markerGroup1" -p "stA_1_1";
	rename -uid "1FEB7E12-4DC5-B50B-999F-83A72AE778D5";
	addAttr -ci true -sn "depth" -ln "depth" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "overscan" -ln "overscan" -dv 1 -min 0 -at "double";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on ".ro";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -l on ".shxy";
	setAttr -l on ".shxz";
	setAttr -l on ".shyz";
	setAttr -l on ".rax";
	setAttr -l on ".ray";
	setAttr -l on ".raz";
	setAttr -k on ".depth";
	setAttr -k on ".overscan";
createNode transform -n "marker_01_MKR" -p "markerGroup1";
	rename -uid "4A7418D1-488B-FB5A-158A-34AB0B29F88D";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" 0.34634864580407732 -0.024614420973117501 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "01";
	setAttr -l on ".markerId" 34;
createNode locator -n "marker_01_MKRShape" -p "marker_01_MKR";
	rename -uid "AAEAD1C1-4DD4-78C6-A72B-949C3B407F0E";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "marker_02_MKR" -p "markerGroup1";
	rename -uid "DD6E09C9-426D-2A95-9FA5-99B093E1FC98";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" -0.05984537086945052 -0.10302597002458069 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "02";
	setAttr -l on ".markerId" 35;
createNode locator -n "marker_02_MKRShape" -p "marker_02_MKR";
	rename -uid "9071AAC0-4DC6-A66C-C7C3-AA96D745D9DD";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "marker_03_MKR" -p "markerGroup1";
	rename -uid "ED594AF2-4143-BC2A-C8E8-3F9AE4175C08";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" 0.0049123859887379995 -0.014922248508412506 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "03";
	setAttr -l on ".markerId" 36;
createNode locator -n "marker_03_MKRShape" -p "marker_03_MKR";
	rename -uid "96BA6D58-4A72-8C75-F032-58AE72E04CF8";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "marker_04_MKR" -p "markerGroup1";
	rename -uid "20B2F594-4407-FAE5-9077-27ABB70CE85A";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" -0.21460628352088096 -0.14764562286544375 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "04";
	setAttr -l on ".markerId" 37;
createNode locator -n "marker_04_MKRShape" -p "marker_04_MKR";
	rename -uid "C1E52C88-46CC-688C-5455-D8B4EDCF3470";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "marker_05_MKR" -p "markerGroup1";
	rename -uid "ED89937C-4A6D-87CD-CC65-2FB1ABBCDAF7";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" 0.36790073696714565 -0.21009571781181824 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "05";
	setAttr -l on ".markerId" 38;
createNode locator -n "marker_05_MKRShape" -p "marker_05_MKR";
	rename -uid "4DA65645-4C6B-4377-D224-8AA83CACF155";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "marker_06_MKR" -p "markerGroup1";
	rename -uid "3A628C85-4453-FC05-2872-94B17B7A29BC";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" 0.40911928575055179 -0.14734680013795254 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "06";
	setAttr -l on ".markerId" 39;
createNode locator -n "marker_06_MKRShape" -p "marker_06_MKR";
	rename -uid "5B1E5036-4757-DA50-86BB-27A3AB8B74D7";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "marker_07_MKR" -p "markerGroup1";
	rename -uid "16442CCB-4894-3B2C-B56D-6DA49C9B2938";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" 0.41054084524885182 0.22418955280575492 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "07";
	setAttr -l on ".markerId" 40;
createNode locator -n "marker_07_MKRShape" -p "marker_07_MKR";
	rename -uid "B55A214B-46AF-0593-84FF-4CBBB0232F04";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "marker_08_MKR" -p "markerGroup1";
	rename -uid "ED7C93AD-4DC1-2501-93C9-73BF273A2ADD";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" -0.16084255950902437 0.21840220670318122 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "08";
	setAttr -l on ".markerId" 41;
createNode locator -n "marker_08_MKRShape" -p "marker_08_MKR";
	rename -uid "99B3ECD0-49B9-E944-86A7-F0A6FF0AFC83";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "marker_09_MKR" -p "markerGroup1";
	rename -uid "A50D499F-443E-1EF8-1A9B-7DB49A438491";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" 0.48380024250737519 0.21900151440599946 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "09";
	setAttr -l on ".markerId" 42;
createNode locator -n "marker_09_MKRShape" -p "marker_09_MKR";
	rename -uid "57F9D9F1-4EF2-3482-734B-40A85A075E86";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "marker_10_MKR" -p "markerGroup1";
	rename -uid "3F769158-4010-2769-93A0-91AE0D08FB05";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" 0.40807291199370599 -0.32617071350988824 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "10";
	setAttr -l on ".markerId" 43;
createNode locator -n "marker_10_MKRShape" -p "marker_10_MKR";
	rename -uid "B04BA69C-4EBA-6071-FE70-4491920B5E0B";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "marker_11_MKR" -p "markerGroup1";
	rename -uid "C25DFB16-4334-FC62-0739-48AF5D99E421";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" 0.4907366314493723 -0.3613093813274636 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "11";
	setAttr -l on ".markerId" 44;
createNode locator -n "marker_11_MKRShape" -p "marker_11_MKR";
	rename -uid "383535EB-453A-775C-2A22-6E9E56517112";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "marker_12_MKR" -p "markerGroup1";
	rename -uid "822C1C58-4DDE-5B0E-2C8D-B892B1E30408";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" -0.34185921228725369 -0.32722472883377646 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "12";
	setAttr -l on ".markerId" 45;
createNode locator -n "marker_12_MKRShape" -p "marker_12_MKR";
	rename -uid "8C9ED63E-44E5-602B-1672-678E685E6437";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "marker_13_MKR" -p "markerGroup1";
	rename -uid "75E0069B-4AFF-E5E8-F53C-4284D9D18EE5";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" 0.060441028938106101 0.45515813508496661 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "13";
	setAttr -l on ".markerId" 46;
createNode locator -n "marker_13_MKRShape" -p "marker_13_MKR";
	rename -uid "B6C4E75A-4663-CAC3-28D6-9890770CA317";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "marker_14_MKR" -p "markerGroup1";
	rename -uid "39AB43E1-41BF-0C89-781C-88B2BAA3F56F";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" 0.48139269071158042 0.46267734398397753 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "14";
	setAttr -l on ".markerId" 47;
createNode locator -n "marker_14_MKRShape" -p "marker_14_MKR";
	rename -uid "AA3374AF-4B92-70CC-01BF-6EBACB81A42B";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "cameraPGroup_pgroup_1_1" -p "Scene";
	rename -uid "B719A0D8-432C-0909-F049-51AB9FF92E5E";
	setAttr ".v" no;
	setAttr ".ro" 2;
createNode transform -n "p01" -p "cameraPGroup_pgroup_1_1";
	rename -uid "B7DD12EB-4B3D-8799-F705-908DEBCE1D14";
	setAttr ".t" -type "double3" 20.105289183210726 1.685647403400971 -24.200849462673361 ;
createNode locator -n "p01Shape" -p "p01";
	rename -uid "6ABD664C-45C5-33CA-72AB-C2BAE13FCF5E";
	setAttr -k off ".v";
createNode transform -n "p02" -p "cameraPGroup_pgroup_1_1";
	rename -uid "C8EDAED3-48C6-D5E9-C8BC-08BC53DEBB29";
	setAttr ".t" -type "double3" -37.985238556118318 -0.78494902004862699 2.7035926333254712 ;
createNode locator -n "p02Shape" -p "p02";
	rename -uid "2CBE4D76-4550-EB13-1510-2EB9028A7DD7";
	setAttr -k off ".v";
createNode transform -n "p03" -p "cameraPGroup_pgroup_1_1";
	rename -uid "F3004393-4BA0-5BE3-C250-EC90408FC1E6";
	setAttr ".t" -type "double3" -20.115517261119265 1.4064757729882731 -52.663909192155401 ;
createNode locator -n "p03Shape" -p "p03";
	rename -uid "D8285E15-4659-C991-A6A5-9C97FB98E81E";
	setAttr -k off ".v";
createNode transform -n "p04" -p "cameraPGroup_pgroup_1_1";
	rename -uid "A61F475F-4F41-C8A0-67E5-C99D4BF3A6AE";
	setAttr ".t" -type "double3" -53.609170892656671 -2.2169311458418068 11.331030012001307 ;
createNode locator -n "p04Shape" -p "p04";
	rename -uid "5569B195-4A69-E21C-83D5-9C8D0F8E5251";
	setAttr -k off ".v";
createNode transform -n "p05" -p "cameraPGroup_pgroup_1_1";
	rename -uid "4CDEE251-487D-444B-6815-069B22903DD3";
	setAttr ".t" -type "double3" -12.69169706187253 -2.115319550159505 43.666317716839188 ;
createNode locator -n "p05Shape" -p "p05";
	rename -uid "6ACF4207-42A5-E831-1B7C-F5BF80C23945";
	setAttr -k off ".v";
createNode transform -n "p06" -p "cameraPGroup_pgroup_1_1";
	rename -uid "17DF2FCC-45E8-1AC8-6B9E-D5A9C1F21528";
	setAttr ".t" -type "double3" 1.0148326244437129 -1.9443485118794031 25.522219881860821 ;
createNode locator -n "p06Shape" -p "p06";
	rename -uid "65254E58-47E9-768B-7464-BF840A3A06F7";
	setAttr -k off ".v";
createNode transform -n "p07" -p "cameraPGroup_pgroup_1_1";
	rename -uid "CEB4B476-4473-8D6A-40AC-F98A7582CE05";
	setAttr ".t" -type "double3" 25.384229828169797 22.999919920425356 -17.656132286918719 ;
createNode locator -n "p07Shape" -p "p07";
	rename -uid "9E68E16D-41C2-A863-E9D4-4EB588E00230";
	setAttr -k off ".v";
createNode transform -n "p08" -p "cameraPGroup_pgroup_1_1";
	rename -uid "1DCBE946-4E69-C422-BFA1-94B8B3D01961";
	setAttr ".t" -type "double3" -43.944182687210514 24.478766890098996 -59.099572174001494 ;
createNode locator -n "p08Shape" -p "p08";
	rename -uid "9482FC15-4C38-A3E7-0E4A-3B86FA5140CF";
	setAttr -k off ".v";
createNode transform -n "p09" -p "cameraPGroup_pgroup_1_1";
	rename -uid "D3D56BC8-4524-688A-3F08-BA979B18A351";
	setAttr ".t" -type "double3" 36.975381409127635 24.401747483359706 2.6642095641371948 ;
createNode locator -n "p09Shape" -p "p09";
	rename -uid "14A1DD77-49E3-C3DB-4381-248562337AAD";
	setAttr -k off ".v";
createNode transform -n "p10" -p "cameraPGroup_pgroup_1_1";
	rename -uid "65D0D03A-45E5-5238-02EA-75B3271ACB40";
	setAttr ".t" -type "double3" 19.944413451710641 -21.226107193809085 -7.3752322286991472 ;
createNode locator -n "p10Shape" -p "p10";
	rename -uid "30682CA3-4637-3F6B-A1F2-E7A75DB2EEF2";
	setAttr -k off ".v";
createNode transform -n "p11" -p "cameraPGroup_pgroup_1_1";
	rename -uid "805FD6A6-4B6A-EEFA-51F3-C2823368399C";
	setAttr ".t" -type "double3" 18.98371274726583 -21.453084303287135 17.576031870174333 ;
createNode locator -n "p11Shape" -p "p11";
	rename -uid "676B5240-4069-A127-AB38-F09C6F8EC228";
	setAttr -k off ".v";
createNode transform -n "p12" -p "cameraPGroup_pgroup_1_1";
	rename -uid "0F84C70D-472D-D265-D6D6-EE9A38E965F8";
	setAttr ".t" -type "double3" -68.476152871427814 -21.952887558155879 -29.061951253047894 ;
createNode locator -n "p12Shape" -p "p12";
	rename -uid "D27BFC56-498A-6C15-84CC-209D01366C31";
	setAttr -k off ".v";
createNode transform -n "p13" -p "cameraPGroup_pgroup_1_1";
	rename -uid "B8F6A948-450D-2619-DDB7-0C97A69B5B74";
	setAttr ".t" -type "double3" -12.545959942972097 46.734941099891252 -48.845022078424236 ;
createNode locator -n "p13Shape" -p "p13";
	rename -uid "4E7DB88A-4852-FFD6-EFF5-3A97E52FAF76";
	setAttr -k off ".v";
createNode transform -n "p14" -p "cameraPGroup_pgroup_1_1";
	rename -uid "D651B7B9-4947-D34E-FB59-E897E7012C3F";
	setAttr ".t" -type "double3" 38.623220506025291 45.213841128842041 12.080218189683592 ;
createNode locator -n "p14Shape" -p "p14";
	rename -uid "4F6CD43B-4CF8-C540-E442-B3A4F09949B9";
	setAttr -k off ".v";
createNode transform -n "bundle_01_BND";
	rename -uid "5FDD32A2-487A-0639-5336-B8BE1F429DD1";
	setAttr ".t" -type "double3" 20.105289183210726 1.685647403400971 -24.200849462673361 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle_01_BNDShape" -p "bundle_01_BND";
	rename -uid "0547210B-40B1-CB38-050D-13AE2758F0BD";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle_02_BND";
	rename -uid "A506F513-4591-15FF-F774-B78DD939C760";
	setAttr ".t" -type "double3" -37.985238556118318 -0.78494902004862699 2.7035926333254712 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle_02_BNDShape" -p "bundle_02_BND";
	rename -uid "715591E9-48BA-7CD7-5B89-32BF89AB860B";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle_03_BND";
	rename -uid "812457E3-4B76-EA21-C1CA-17A1C6FE04F8";
	setAttr ".t" -type "double3" -20.115517261119265 1.4064757729882731 -52.663909192155401 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle_03_BNDShape" -p "bundle_03_BND";
	rename -uid "D8283B06-413F-2F67-5DD3-14A5E97D8A36";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle_04_BND";
	rename -uid "FB6A8515-453C-3E9B-31BD-E187D8758CAF";
	setAttr ".t" -type "double3" -53.609170892656671 -2.2169311458418068 11.331030012001307 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle_04_BNDShape" -p "bundle_04_BND";
	rename -uid "83A891C5-42D0-14FF-25AD-A9B68D44792F";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle_05_BND";
	rename -uid "AFB6C13C-4827-98AF-5516-4AB9C17C15A3";
	setAttr ".t" -type "double3" -12.69169706187253 -2.115319550159505 43.666317716839188 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle_05_BNDShape" -p "bundle_05_BND";
	rename -uid "94D8CE36-460A-720B-17B5-D8B5AAD35C69";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle_06_BND";
	rename -uid "4D5869D5-4FFF-F30E-623D-CDB1CD91D8F5";
	setAttr ".t" -type "double3" 1.0148326244437129 -1.9443485118794031 25.522219881860821 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle_06_BNDShape" -p "bundle_06_BND";
	rename -uid "76E20B02-415A-7E82-3434-918EBFD2169B";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle_07_BND";
	rename -uid "0C5E3555-4C11-EBD3-E3B2-37B9C14A9FDC";
	setAttr ".t" -type "double3" 25.384229828169797 22.999919920425356 -17.656132286918719 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle_07_BNDShape" -p "bundle_07_BND";
	rename -uid "FF7A6D4F-4AD9-71FB-A007-CAB07DE12568";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle_08_BND";
	rename -uid "6CB57822-4A42-9C78-BF34-F29E0BE85C70";
	setAttr ".t" -type "double3" -43.944182687210514 24.478766890098996 -59.099572174001494 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle_08_BNDShape" -p "bundle_08_BND";
	rename -uid "E72D4A25-4AB0-B456-AE66-F8BA97466551";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle_09_BND";
	rename -uid "56B8E183-4F8E-3134-A418-45BC0C781290";
	setAttr ".t" -type "double3" 36.975381409127635 24.401747483359706 2.6642095641371948 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle_09_BNDShape" -p "bundle_09_BND";
	rename -uid "EBBE451E-4945-3C77-D11C-D0A6983D3C74";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle_10_BND";
	rename -uid "79E3406C-4B86-DDFD-2350-1197F217D3A8";
	setAttr ".t" -type "double3" 19.944413451710641 -21.226107193809085 -7.3752322286991472 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle_10_BNDShape" -p "bundle_10_BND";
	rename -uid "8ED36276-4243-F3A9-4AA0-3BBF247B95D7";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle_11_BND";
	rename -uid "C622255E-4E78-B414-4F88-7D980D6CDE3F";
	setAttr ".t" -type "double3" 18.98371274726583 -21.453084303287135 17.576031870174333 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle_11_BNDShape" -p "bundle_11_BND";
	rename -uid "90B46965-417E-F539-34C0-DEB9021712AE";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle_12_BND";
	rename -uid "7BAC205E-4887-9448-A388-08AB58FBC62E";
	setAttr ".t" -type "double3" -68.476152871427814 -21.952887558155879 -29.061951253047894 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle_12_BNDShape" -p "bundle_12_BND";
	rename -uid "192B584F-4DB7-6388-7E79-05959FAC95A4";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle_13_BND";
	rename -uid "700EB63C-47CE-DB48-2473-5383166C4B43";
	setAttr ".t" -type "double3" -12.545959942972097 46.734941099891252 -48.845022078424236 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle_13_BNDShape" -p "bundle_13_BND";
	rename -uid "76BCFA8E-41A4-3644-A006-FC9BE667948D";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle_14_BND";
	rename -uid "00DBA3A8-4AE7-7A73-36CA-5EACCAD821F6";
	setAttr ".t" -type "double3" 38.623220506025291 45.213841128842041 12.080218189683592 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle_14_BNDShape" -p "bundle_14_BND";
	rename -uid "2B6A05C9-4DFA-8348-80C1-51BBC7DDCDA8";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "1A6BC8C8-4BA8-556F-645F-DAA1D3EC0BE5";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "B66854A4-42EF-E83F-2C5F-32A51D3D527F";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "DAFA6D2E-4371-E9E5-7123-3692099A9D9D";
createNode displayLayerManager -n "layerManager";
	rename -uid "28880919-4171-6251-4737-5CBDBDC0D187";
createNode displayLayer -n "defaultLayer";
	rename -uid "ACE46573-4E98-0B71-47EA-7BBF395E7A31";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "6CECC3E3-4F3A-8763-68A5-BAA723F6FEB6";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "6E09CB4E-4F77-34A9-DD64-0DB4432C21F5";
	setAttr ".g" yes;
createNode expression -n "frame_ext_expression";
	rename -uid "C2B6BC1F-4190-E253-BBD6-74A2D08C2BBD";
	setAttr -k on ".nds";
	setAttr ".ixp" -type "string" ".O[0]=frame";
createNode animCurveTL -n "stA_1_1_translateX";
	rename -uid "F798B7AB-4D55-8256-F631-4BA1D2729FDC";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 -18.129932091973817 1 -18.654239137830956
		 2 -19.268517494662611 3 -20.02657478708236 4 -20.943081755403757 5 -21.994759667068628
		 6 -23.149286851138282 7 -24.371789468504236 8 -25.628204498545315 9 -26.901360148962379
		 10 -28.172345633877036 11 -29.435414575574399 12 -30.70353666514433 13 -31.977387049309133
		 14 -33.270778029587916 15 -34.597069050879718 16 -35.948454004727729 17 -37.319422346567663
		 18 -38.70809693625386 19 -40.114436181480819 20 -41.541989223140227 21 -42.990934021963916
		 22 -44.454852415814642 23 -45.920525201827317 24 -47.37339254399123 25 -48.802458066083929
		 26 -50.207138993855537 27 -51.601776511618567 28 -53.007262244118962 29 -54.441608096606529
		 30 -55.91282557129442 31 -57.415823935032485 32 -58.938340313824824 33 -60.470100710819814
		 34 -62.002896845156158 35 -63.525942025795629 36 -65.029251410050122 37 -66.509988608881443
		 38 -67.973411521563563 39 -69.422234385812047 40 -70.85314682554565 41 -72.271266816303807
		 42 -73.691667236318821 43 -75.123366719229708 44 -76.560240044340446 45 -77.990282236189529
		 46 -79.409052792156402 47 -80.819560586917163 48 -82.226806124816434 49 -83.637758482460143
		 50 -85.064062538735499 51 -86.516210179108469 52 -87.991860797045049 53 -89.478755386523758
		 54 -90.967050018156513 55 -92.451116563075715 56 -93.926223485660586 57 -95.391560948676755
		 58 -96.849095108554877 59 -98.298369620053805 60 -99.739657682713244 61 -101.1649693405995
		 62 -102.5562657487442 63 -103.89894407101248 64 -105.18932099669077 65 -106.44753212738969
		 66 -107.70742848853534 67 -108.98724829671852 68 -110.28500267989824 69 -111.58355857178513
		 70 -112.86230958426225 71 -114.11250819072829 72 -115.3360662532787 73 -116.54685224505312
		 74 -117.7685371162478 75 -119.01863942941478 76 -120.29677605598619 77 -121.58442035466722
		 78 -122.8551623108186 79 -124.09291467638168 80 -125.29539137733985 81 -126.46436789679278
		 82 -127.60911612211066 83 -128.73432269524491 84 -129.83424030692655 85 -130.91471577821019
		 86 -131.97901736583032 87 -133.0194723253029 88 -134.02470970279575 89 -134.98893019125487
		 90 -135.92771498802699 91 -136.85480426290241 92 -137.76700734543266 93 -138.66352854200886
		 94 -139.54845749097862;
createNode animCurveTL -n "stA_1_1_translateY";
	rename -uid "A3461D88-4F12-893B-A804-86A64540CF2B";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 13.456012366844796 1 13.45536497121863
		 2 13.454028138970493 3 13.452944630642818 4 13.453608675297369 5 13.455317977679215
		 6 13.455379290019346 7 13.452602869985219 8 13.447931794256231 9 13.442195376671739
		 10 13.435467827379247 11 13.427283883588514 12 13.417130825807677 13 13.404709686017219
		 14 13.389528167939293 15 13.37306896513469 16 13.358532416700678 17 13.346875536294782
		 18 13.336546596270418 19 13.325252702921402 20 13.311302809708835 21 13.294704467195059
		 22 13.276388041696913 23 13.257723543721037 24 13.240539446170612 25 13.225919627574973
		 26 13.21305023735499 27 13.199250762421345 28 13.182170003953585 29 13.162036150542155
		 30 13.141014482866144 31 13.120982704074125 32 13.102524748267081 33 13.085869387554345
		 34 13.071676805532794 35 13.060605683416671 36 13.052971941533142 37 13.048674649887769
		 38 13.047419981527566 39 13.047439004667856 40 13.044630785388005 41 13.036451687998909
		 42 13.024098396343339 43 13.010119003583124 44 12.996321070676776 45 12.983618598336028
		 46 12.97254545149641 47 12.961928250430006 48 12.949215516778656 49 12.933721877548635
		 50 12.915698857253515 51 12.895479087183054 52 12.873850252698071 53 12.85088818703446
		 54 12.82610915818643 55 12.798742930155928 56 12.768739368687612 57 12.738170475886047
		 58 12.709116969814891 59 12.682050365554032 60 12.656908638411275 61 12.633267352655679
		 62 12.609649489982173 63 12.582051854186913 64 12.546187621922702 65 12.50408978262347
		 66 12.463219900487992 67 12.427772939744868 68 12.396501781195688 69 12.367543109692534
		 70 12.340348226926968 71 12.312937015822099 72 12.281318530250276 73 12.244011016780515
		 74 12.20474498602548 75 12.169247975887018 76 12.140669980106283 77 12.11883777266763
		 78 12.102564097455945 79 12.090177909539578 80 12.078895768906225 81 12.066569629224444
		 82 12.05205424451308 83 12.031632167216582 84 12.000433065252466 85 11.96166465274864
		 86 11.925451705114545 87 11.89460745108334 88 11.863105897088516 89 11.829418601393888
		 90 11.80044688829893 91 11.78144466943594 92 11.770043948164727 93 11.76066677969151
		 94 11.750464018613229;
createNode animCurveTL -n "stA_1_1_translateZ";
	rename -uid "7574D845-4A6E-CF02-81C8-30A0362DE30C";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 120.72150868173213 1 120.81960447165096
		 2 120.93494444060528 3 121.08478931456111 4 121.28079851273853 5 121.51502648563981
		 6 121.76347030413694 7 122.0088789028818 8 122.24775080335101 9 122.47797950981973
		 10 122.69367976477533 11 122.89193744918967 12 123.07462301927357 13 123.24498694238966
		 14 123.40549672397455 15 123.55924002644821 16 123.71051680506649 17 123.85936116298085
		 18 124.00370756567784 19 124.1415287114034 20 124.26815223209425 21 124.38299588271356
		 22 124.48735175476097 23 124.57983133172415 24 124.66394698319853 25 124.74049774493898
		 26 124.80612280288742 27 124.85831675640598 28 124.88948424172902 29 124.89708740820768
		 30 124.887081154912 31 124.86169707070925 32 124.82035599593078 33 124.76317520946415
		 34 124.69305000181532 35 124.6174201711445 36 124.5362108407533 37 124.44328307089808
		 38 124.33879125033901 39 124.21924153837375 40 124.07792544258298 41 123.91504173015426
		 42 123.73466190999306 43 123.5430539160938 44 123.3410355047339 45 123.11944260682172
		 46 122.87508404857816 47 122.60728787211772 48 122.31299221761755 49 122.00116999741381
		 50 121.67266017357933 51 121.32100241024722 52 120.94320277704281 53 120.52942368625664
		 54 120.07218258194217 55 119.56716049686358 56 119.0095115413345 57 118.41241343289154
		 58 117.7933897524329 59 117.15800109298335 60 116.51369059120202 61 115.85902166292034
		 62 115.18885557783044 63 114.50187264136913 64 113.78791888572911 65 113.04304095975638
		 66 112.27330375913813 67 111.47632696696152 68 110.65122821135861 69 109.80351909252322
		 70 108.93619190214159 71 108.0503904668586 72 107.13275196407209 73 106.169623530244
		 74 105.16521036141295 75 104.11515187559466 76 103.01495207715563 77 101.87825552408991
		 78 100.72059288677687 79 99.557156334473689 80 98.389788465062708 81 97.200920829955678
		 82 95.982262554559924 83 94.721162965423588 84 93.401494076235451 85 92.035247111853764
		 86 90.631740350719681 87 89.18023384961829 88 87.662404351675633 89 86.081823041582396
		 90 84.482946984050443 91 82.901935128492269 92 81.341142025841364 93 79.796754870359621
		 94 78.262320649270421;
createNode animCurveTA -n "stA_1_1_rotateX";
	rename -uid "D47B1A65-4209-4734-4297-21A973DC44F9";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 -3.427202632122659 1 -3.4541086733531778
		 2 -3.480329686438608 3 -3.558576490056045 4 -3.5986948413243645 5 -3.5924829264427851
		 6 -3.557594938130245 7 -3.5607633101634089 8 -3.5355706169473904 9 -3.518287324132185
		 10 -3.475725660314684 11 -3.4644307397217071 12 -3.4716922324282069 13 -3.4823593831372648
		 14 -3.4999313938444461 15 -3.510390797547799 16 -3.4877717158005641 17 -3.4809956284472969
		 18 -3.4611454694212438 19 -3.4274531116349229 20 -3.4123684732357309 21 -3.4001851189872561
		 22 -3.385607661580758 23 -3.384111302358463 24 -3.3511646519236602 25 -3.3301472523412601
		 26 -3.299608125880976 27 -3.2373342150115789 28 -3.209428837378586 29 -3.2328794102141241
		 30 -3.2522756056775619 31 -3.2420265958882428 32 -3.2281564311577045 33 -3.2066324739428915
		 34 -3.234041212630971 35 -3.2000768419059029 36 -3.106454125628348 37 -3.0573150045856989
		 38 -3.0310248559090791 39 -2.9841849632226798 40 -2.953553620514358 41 -2.9536683785556468
		 42 -2.9502225705041112 43 -2.9346067814341539 44 -2.8957853919404228 45 -2.8352620645222451
		 46 -2.8421069670472869 47 -2.8407718918367806 48 -2.8732326484394659 49 -2.893411709212752
		 50 -2.8795282192901714 51 -2.8813073268080212 52 -2.8093758038203949 53 -2.7467289856092258
		 54 -2.675888647753589 55 -2.63026860972148 56 -2.664951716491081 57 -2.722507755785553
		 58 -2.7718574684731592 59 -2.7344672364463789 60 -2.7158509839009839 61 -2.6380256793791901
		 62 -2.587912167883637 63 -2.5054627517342105 64 -2.4500216155320911 65 -2.4247529045201688
		 66 -2.4530441543247541 67 -2.4288734242108729 68 -2.374854166705664 69 -2.3603563550741762
		 70 -2.3542202382975539 71 -2.3327463497841681 72 -2.3001992855313991 73 -2.3003901414000438
		 74 -2.3214131634097819 75 -2.3390310605973039 76 -2.3085319131253272 77 -2.2806221296253781
		 78 -2.2782653309220167 79 -2.2561109053722941 80 -2.184948784089737 81 -2.1546519506951598
		 82 -2.1057959520617011 83 -2.093832786645478 84 -2.1109920948649359 85 -2.1385120000851541
		 86 -2.1604129374427958 87 -2.1157975632622068 88 -2.0690539562505599 89 -2.0515296463953381
		 90 -2.070810411962293 91 -2.126163024196595 92 -2.130534867511837 93 -2.077378338139007
		 94 -2.0034499475967138;
createNode animCurveTA -n "stA_1_1_rotateY";
	rename -uid "97757D58-4DB2-B1F7-EA4A-248AEDB49486";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 1.213529880665916 1 1.064267207727525
		 2 0.89254165361027804 3 0.67603641699296102 4 0.38967430670507103 5 0.090477690104959999
		 6 -0.26746631040496399 7 -0.65221648562732715 8 -1.05533264404047 9 -1.4815763445343251
		 10 -1.8856298274717571 11 -2.2360423393660596 12 -2.6360651250081659 13 -2.9998731469460531
		 14 -3.4511728324413511 15 -3.855689085249733 16 -4.2823890774337006 17 -4.7340412739775628
		 18 -5.2328038339523806 19 -5.7231554085020857 20 -6.2168193049001923 21 -6.6945257441295176
		 22 -7.2343970777418223 23 -7.7559466318679062 24 -8.2444874130711163 25 -8.712239124927482
		 26 -9.2415985106426746 27 -9.7204119516437757 28 -10.170636584801114 29 -10.671600884115069
		 30 -11.177803991683643 31 -11.695942281592863 32 -12.272385417869344 33 -12.802433594177423
		 34 -13.338685369908445 35 -13.916850110649424 36 -14.439360666159374 37 -14.943407374575905
		 38 -15.475939193297702 39 -16.044579162299936 40 -16.610599915184967 41 -17.206263748503307
		 42 -17.763619041207726 43 -18.311541424985947 44 -18.900282060928085 45 -19.448523797815685
		 46 -19.997864198520428 47 -20.581960920267356 48 -21.163145764211254 49 -21.748364537434789
		 50 -22.424752406550549 51 -23.068685871571851 52 -23.894905121993311 53 -24.861592651030612
		 54 -25.906131319020052 55 -26.957413013507658 56 -27.996613678108652 57 -29.031217681410983
		 58 -30.111390214274145 59 -31.210576621801849 60 -32.280654781668694 61 -33.348364443372596
		 62 -34.386742560135993 63 -35.422692217896895 64 -36.449052876779035 65 -37.433047055815585
		 66 -38.467759023530718 67 -39.510600049885966 68 -40.56908622175051 69 -41.61542359163527
		 70 -42.723712950602277 71 -43.845534091866107 72 -44.871640360929455 73 -45.946495164944778
		 74 -47.070292879195819 75 -48.251005313509118 76 -49.384338801286944 77 -50.601855031439818
		 78 -51.801380114299093 79 -52.979302634132118 80 -54.133913192552697 81 -55.240576202599556
		 82 -56.371697656707497 83 -57.544519274657297 84 -58.718404319821346 85 -59.872597424473909
		 86 -61.116647580228388 87 -62.336398225475868 88 -63.558938488845236 89 -64.821308140711466
		 90 -66.078602692758153 91 -67.310312078910883 92 -68.590356742530957 93 -69.866220104604238
		 94 -71.110279801497711;
createNode animCurveTA -n "stA_1_1_rotateZ";
	rename -uid "3754F201-48BC-AB14-4866-F1B80C003E8E";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 -0.23813625306952096 1 -0.213435899077243
		 2 -0.221051333541952 3 -0.22119076340322499 4 -0.19696743745131901 5 -0.17782824621641199
		 6 -0.167426491265109 7 -0.17083650338561601 8 -0.17520816720833801 9 -0.16022746824516901
		 10 -0.101315900255006 11 -0.053003968360002998 12 -0.030024497175667002 13 0.021153533892003001
		 14 0.032521931453194 15 0.081879106675901994 16 0.170782663963153 17 0.216628150875155
		 18 0.23626601851536702 19 0.25722142973059298 20 0.22510089245170903 21 0.22075966407779099
		 22 0.172252538272328 23 0.13831906460496901 24 0.084986283313187999 25 0.059459614120671994
		 26 -0.013279439095913 27 -0.090979965372683005 28 -0.11346849405944801 29 -0.16698582747411
		 30 -0.19902884728648804 31 -0.17215251436564699 32 -0.16494289218915401 33 -0.15717167143916899
		 34 -0.097520199147678996 35 -0.092992609320930994 36 -0.091057226934264004 37 -0.091052985643173004
		 38 -0.069211701894435998 39 -0.027024182622366 40 -0.0074908868382049989 41 -0.050897101022040002
		 42 -0.067123138999286999 43 -0.049925622039830003 44 -0.091691953435325005 45 -0.095953227241550018
		 46 -0.13322373934759399 47 -0.191332423157173 48 -0.17041993028577401 49 -0.15954769611851999
		 50 -0.17671533671418199 51 -0.20212144139104499 52 -0.16421951605674601 53 -0.102677711279329
		 54 -0.067298382706136001 55 -0.068410378520180004 56 -0.00024167679737900001 57 0.044116992514864999
		 58 0.085344857784958997 59 0.092311431574912006 60 0.13139830968428101 61 0.192861187770341
		 62 0.19478854711024102 63 0.23501904261285703 64 0.20915544571521899 65 0.18555198495575001
		 66 0.180273426705294 67 0.16843581201602101 68 0.16037568794023799 69 0.130855994585721
		 70 0.098373317280535 71 0.087767978585869003 72 0.079082070450240002 73 0.050625738208529003
		 74 0.054434925075731999 75 0.064999543323594006 76 0.063758717627521999 77 0.045498418908461999
		 78 0.064696918869383002 79 0.075935454433805005 80 0.079434307825972994 81 0.085929016592731999
		 82 0.084972686973108003 83 0.043647412224976999 84 0.042245882400415997 85 0.041747298952368998
		 86 0.027833244142110001 87 0.023519857347011001 88 0.027578499266999002 89 -0.020986271686763001
		 90 -0.049225689979872998 91 -0.060747968200303003 92 -0.052658794192902002 93 -0.077875226491470995
		 94 -0.104459598651383;
createNode animCurveTU -n "stA_1_1Shape1_focalLength";
	rename -uid "3BC65EAC-42C9-5A4E-EF6C-628BCA393C87";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 27.18375 1 27.18375 2 27.18375 3 27.18375
		 4 27.18375 5 27.18375 6 27.18375 7 27.18375 8 27.18375 9 27.18375 10 27.18375 11 27.18375
		 12 27.18375 13 27.18375 14 27.18375 15 27.18375 16 27.18375 17 27.18375 18 27.18375
		 19 27.18375 20 27.18375 21 27.18375 22 27.18375 23 27.18375 24 27.18375 25 27.18375
		 26 27.18375 27 27.18375 28 27.18375 29 27.18375 30 27.18375 31 27.18375 32 27.18375
		 33 27.18375 34 27.18375 35 27.18375 36 27.18375 37 27.18375 38 27.18375 39 27.18375
		 40 27.18375 41 27.18375 42 27.18375 43 27.18375 44 27.18375 45 27.18375 46 27.18375
		 47 27.18375 48 27.18375 49 27.18375 50 27.18375 51 27.18375 52 27.18375 53 27.18375
		 54 27.18375 55 27.18375 56 27.18375 57 27.18375 58 27.18375 59 27.18375 60 27.18375
		 61 27.18375 62 27.18375 63 27.18375 64 27.18375 65 27.18375 66 27.18375 67 27.18375
		 68 27.18375 69 27.18375 70 27.18375 71 27.18375 72 27.18375 73 27.18375 74 27.18375
		 75 27.18375 76 27.18375 77 27.18375 78 27.18375 79 27.18375 80 27.18375 81 27.18375
		 82 27.18375 83 27.18375 84 27.18375 85 27.18375 86 27.18375 87 27.18375 88 27.18375
		 89 27.18375 90 27.18375 91 27.18375 92 27.18375 93 27.18375 94 27.18375;
createNode mmMarkerScale -n "mmMarkerScale1";
	rename -uid "1DD173A6-42BF-918D-A5B2-58AF644EBD77";
createNode animCurveTL -n "marker_01_MKR_translateX";
	rename -uid "EF5B029E-409D-506E-5308-DDA97FDF896B";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 56 ".ktv[0:55]"  0 0.34864986654119756 1 0.34967451962007989
		 2 0.35073183216176895 3 0.35180961814456235 4 0.35253393343818029 5 0.35376106322854473
		 6 0.35452948959406938 7 0.35519409784709921 8 0.35562467196456427 9 0.35561754061851236
		 10 0.3560706319992617 11 0.35777717452859326 12 0.35828200915190667 13 0.35961585306364907
		 14 0.35918255355312989 15 0.35995450622606273 16 0.36023907995894366 17 0.36009443550417974
		 18 0.35890786300053146 19 0.35799430009795064 20 0.35715952922274619 21 0.35679626638390638
		 22 0.35498897881377534 23 0.35363102515555411 24 0.35282652351188026 25 0.35229343607024344
		 26 0.35023248046832012 27 0.34916518543361552 28 0.34881290632991468 29 0.34757875670803218
		 30 0.34634864580407732 31 0.34498982970429537 32 0.34250281863131393 33 0.34108918409859612
		 34 0.33950001227613369 35 0.33681104326529998 36 0.33518981027914774 37 0.33392757729581224
		 38 0.33192660331693302 78 -0.063161033466632932 79 -0.077420096064584665 80 -0.091450711991579448
		 81 -0.10450696191419623 82 -0.11806830512927868 83 -0.13241573383931809 84 -0.14668030399091753
		 85 -0.16027819150406492 86 -0.17574706993915878 87 -0.19057469993881798 88 -0.20520910111105212
		 89 -0.22031966958845461 90 -0.2356242324957985 91 -0.25062706878831581 92 -0.2669137982960984
		 93 -0.28335659047651207 94 -0.29918590555492219;
createNode animCurveTL -n "marker_01_MKR_translateY";
	rename -uid "6250B111-402F-B95B-BBB9-A1A9CDD07186";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 56 ".ktv[0:55]"  0 -0.037690170832632819 1 -0.036719001104219606
		 2 -0.035496529340060035 3 -0.032671217163490529 4 -0.031230956110795072 5 -0.031224746920587076
		 6 -0.031958920491857612 7 -0.031289376415875703 8 -0.031493692681092367 9 -0.031565358197539417
		 10 -0.032911173762810442 11 -0.033048683894211506 12 -0.032418353666527733 13 -0.031926513320563399
		 14 -0.030659077608836738 15 -0.030035378541598823 16 -0.030958813316920131 17 -0.030868604100777908
		 18 -0.030970568869392312 19 -0.031494640729673173 20 -0.030934925126086588 21 -0.030485697836063474
		 22 -0.029703231263266794 23 -0.028674282354412772 24 -0.028483595731903399 25 -0.028209696929935801
		 26 -0.027747051315591686 27 -0.028320367478005426 28 -0.028307927558420543 29 -0.026304395134832959
		 30 -0.024614420973117501 31 -0.024461566231507359 32 -0.024201265366252722 33 -0.024244492737864387
		 34 -0.023255976255336652 35 -0.023665980539011144 36 -0.026105260540686459 37 -0.027142675407426986
		 38 -0.027698572729690063 78 -0.027672107047196859 79 -0.02821657573727343 80 -0.030331553705489123
		 81 -0.031181095571691797 82 -0.032624283238956053 83 -0.032950510324115001 84 -0.032168214522744765
		 85 -0.030804991941015269 86 -0.029907525152316039 87 -0.031204361462227492 88 -0.032576257721875113
		 89 -0.033364005340048464 90 -0.032883608296028877 91 -0.031271345147220575 92 -0.031294488320270653
		 93 -0.033416998841453549 94 -0.03625914698227839;
createNode animCurveTU -n "marker_01_MKR_enable";
	rename -uid "2870B792-45EE-6E24-32A8-DEB7EB965C1C";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 1 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 0 40 0 41 0 42 0 43 0
		 44 0 45 0 46 0 47 0 48 0 49 0 50 0 51 0 52 0 53 0 54 0 55 0 56 0 57 0 58 0 59 0 60 0
		 61 0 62 0 63 0 64 0 65 0 66 0 67 0 68 0 69 0 70 0 71 0 72 0 73 0 74 0 75 0 76 0 77 0
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1;
createNode animCurveTU -n "marker_01_MKR_weight";
	rename -uid "8807D5FB-4C82-710C-37C3-30AC0FBCC635";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 56 ".ktv[0:55]"  0 1 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 78 1 79 1 80 1 81 1 82 1
		 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1;
createNode animCurveTL -n "marker_02_MKR_translateX";
	rename -uid "1D575A7B-481E-973F-1152-959642E633AE";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 -0.17802311720040814 1 -0.17584835758112444
		 2 -0.17315880538532719 3 -0.16995918764640328 4 -0.16654244817978781 5 -0.16202917811960266
		 6 -0.15767954068586815 7 -0.15318933313258637 8 -0.1487587653814772 9 -0.14463088472402247
		 10 -0.14023934727745685 11 -0.13483222520434496 12 -0.13037458269409263 13 -0.12512151148352446
		 14 -0.12161264231659052 15 -0.11672716513302184 16 -0.11223426723211705 17 -0.1080998447709971
		 18 -0.10472696206260573 19 -0.10100235226066584 20 -0.097198373294083429 21 -0.092856826822086735
		 22 -0.089652911916769273 23 -0.086085647560919354 24 -0.08195548064656244 25 -0.077656087374102512
		 26 -0.075011309975424323 27 -0.071339394930246769 28 -0.06706678907261443 29 -0.06363815571924708
		 30 -0.05984537086945052 31 -0.056115250687112317 32 -0.053504263615935688 33 -0.049766687163574574
		 34 -0.046293060864810942 35 -0.043790065712325299 36 -0.04026228248836905 37 -0.036720693650453273
		 38 -0.033972726811846043 39 -0.032069613529889851 40 -0.030357792271965722 41 -0.029323063645804615
		 42 -0.027509882400372221 43 -0.025352018774197738 44 -0.023938456842458766 45 -0.021838505073642045
		 46 -0.019800836138821554 47 -0.018529043138758416 48 -0.017260833854340962 49 -0.016063634139480532
		 50 -0.016644269232254538 51 -0.016252822871600126 52 -0.01945078190423366 53 -0.025678728851647736
		 54 -0.03338296420269099 55 -0.041056883828491486 56 -0.048467915068055367 57 -0.055681742702747006
		 58 -0.063936116923260844 59 -0.07252015875462664 60 -0.08062806951258511 61 -0.088777383593881487
		 62 -0.096432765738835635 63 -0.10455607344821832 64 -0.11260341950931463 65 -0.11984295489827113
		 66 -0.12821592151005612 67 -0.13627913478927783 68 -0.14455559691676784 69 -0.15234231262562326
		 70 -0.16152179360983587 71 -0.17126845757902442 72 -0.17888325029442653 73 -0.18750592427534801
		 74 -0.19685514848090657 75 -0.20708056032167793 76 -0.21551566777293513 77 -0.22555792519473705
		 78 -0.23527346263881366 79 -0.24483793453526198 80 -0.25407390945927527 81 -0.2623989307691415
		 82 -0.27120081818062769 83 -0.28069422248712683 84 -0.29001131805151048 85 -0.29864629480339777
		 86 -0.30916435827309485 87 -0.31886859315130245 88 -0.32836896253757641 89 -0.33822826950860074
		 90 -0.34818059203241075 91 -0.35778091602525786 92 -0.36873328655313997 93 -0.37976143444145877
		 94 -0.39030361847545691;
createNode animCurveTL -n "marker_02_MKR_translateY";
	rename -uid "32935E84-4CC0-1224-DD2D-8983D7288010";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 -0.1103833817579648 1 -0.10950211947745386
		 2 -0.10853401985508498 3 -0.10579884735082073 4 -0.10423995553433651 5 -0.10451623057266185
		 6 -0.10518319219979877 7 -0.10477547849121965 8 -0.10520783784215976 9 -0.10551742860510421
		 10 -0.10625625538041694 11 -0.10597406973422085 12 -0.10524693383146794 13 -0.10435820194514872
		 14 -0.10327951267956909 15 -0.10233008882312616 16 -0.10226995825609364 17 -0.10192362591947102
		 18 -0.10211741051818796 19 -0.10289080327739297 20 -0.10276714966199002 21 -0.10265738412613601
		 22 -0.10265719992564504 23 -0.1022243819795669 24 -0.10262925442752552 25 -0.10286721121183667
		 26 -0.10354356653781643 27 -0.10512670337337621 28 -0.10546328649709097 29 -0.10406759957201184
		 30 -0.10302597002458069 31 -0.10246183821558486 32 -0.1022055106918156 33 -0.10245421808134403
		 34 -0.10074989699841008 35 -0.101254796084775 36 -0.10386408468201508 37 -0.10500184082380143
		 38 -0.10528671531715927 39 -0.10649652611584021 40 -0.1069883370914273 41 -0.10662176811867174
		 42 -0.10619298386260662 43 -0.1060208692068968 44 -0.10677196778020326 45 -0.1081922409409467
		 46 -0.10750629778846627 47 -0.10709460573897062 48 -0.1055806780113791 49 -0.10426956122163644
		 50 -0.1042242300836006 51 -0.10350677811021819 52 -0.10516648050971622 53 -0.10666059087650615
		 54 -0.10821737794857289 55 -0.10904016096889957 56 -0.10724799948836472 57 -0.10478655662171921
		 58 -0.10262799826942981 59 -0.10317603370243389 60 -0.10335282653524436 61 -0.10531342027190044
		 62 -0.10640906846296411 63 -0.10857131628711425 64 -0.10995066397309672 65 -0.11006606328712115
		 66 -0.10877692806146544 67 -0.10911264523029368 68 -0.11039902276835667 69 -0.110666399792542
		 70 -0.11062462207943624 71 -0.11114491076497585 72 -0.11210773272173419 73 -0.11193009935514181
		 74 -0.11088430316649289 75 -0.10985521208960286 76 -0.11089677576692025 77 -0.11180924122902164
		 78 -0.11178979657028065 79 -0.11277978060129151 80 -0.11527158810208216 81 -0.11628062729762145
		 82 -0.11797544365570095 83 -0.11882654946059645 84 -0.11849055592070673 85 -0.11725778627082695
		 86 -0.11675926511933304 87 -0.11841228595167658 88 -0.12019667823690255 89 -0.12147990624308636
		 90 -0.121596833210811 91 -0.12043289715193484 92 -0.12091955914075558 93 -0.12349768792112542
		 94 -0.12664028779348768;
createNode animCurveTU -n "marker_02_MKR_enable";
	rename -uid "0C012014-4E50-2459-F69C-CEA0F4567643";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 1 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1;
createNode animCurveTU -n "marker_02_MKR_weight";
	rename -uid "A17B42E7-4C07-DFCD-DF07-509878810124";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 1 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1;
createNode animCurveTL -n "marker_03_MKR_translateX";
	rename -uid "7B74FD05-407D-9AC1-8EAD-59A3058E72AB";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 70 ".ktv[0:69]"  15 0.017281123092361184 16 0.017430507900541015
		 17 0.017229809868597235 18 0.016059278472440819 19 0.015191134884128599 20 0.014359004045365165
		 21 0.013970113677576945 22 0.012317286445286291 23 0.011029092610656321 24 0.010392313621261029
		 25 0.0099245389671507311 26 0.0081027324890421415 27 0.0072452884647167259 28 0.0070402374693131486
		 29 0.0059736145847060218 30 0.0049123859887379995 31 0.0038238210993838395 32 0.0016590747096373315
		 33 0.0004891180120966121 34 -0.0008671111968925338 35 -0.0031191281222069378 36 -0.0043841632570140732
		 37 -0.0053498223550748625 38 -0.0070487827944908377 39 -0.0095911377515206508 40 -0.012214609603029336
		 41 -0.015507169532235909 42 -0.018017755746687014 43 -0.020293021401911693 44 -0.023394219369121505
		 45 -0.025640620675071835 46 -0.027920298438163849 47 -0.031029383603076943 48 -0.03407000827143547
		 49 -0.037099499913782308 50 -0.041933530975900413 51 -0.045894827557602602 52 -0.053622344832338964
		 53 -0.064335688710470018 54 -0.076477830012265657 55 -0.088799574235187306 56 -0.10087978243591
		 57 -0.11282190476479548 58 -0.12578747843774857 59 -0.13905426405059207 60 -0.15189007321774622
		 61 -0.16471810682306726 62 -0.1770670579714626 63 -0.18962811440917765 64 -0.20217691079752692
		 65 -0.21385411589546388 66 -0.22668378013078472 67 -0.23950329436035905 68 -0.25249806917836032
		 69 -0.26526115550950347 70 -0.27944596998146121 71 -0.29405620726642767 72 -0.30658870465778076
		 73 -0.32006778455168261 74 -0.33456804861989703 75 -0.35008631496580112 76 -0.36435279853752656
		 77 -0.38039966422083926 78 -0.39607607484994611 79 -0.41151175402572687 80 -0.42658590635319105
		 81 -0.44076376623885322 82 -0.4556299194374705 83 -0.47139131721608601 84 -0.4871981716387645;
createNode animCurveTL -n "marker_03_MKR_translateY";
	rename -uid "9FADDBA3-4C89-EAB4-526A-9FAE462F102B";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 70 ".ktv[0:69]"  15 -0.012089477243869995 16 -0.012511747064940459
		 17 -0.012429835355646568 18 -0.012772667282497208 19 -0.013508089956533076 20 -0.013645063031165972
		 21 -0.013646881629861551 22 -0.013677919635428692 23 -0.013325554177212706 24 -0.014013640301787034
		 25 -0.014290901021683899 26 -0.014891309297436817 27 -0.016575662939752545 28 -0.017108740106099141
		 29 -0.015974946101352472 30 -0.014922248508412506 31 -0.014880987004904922 32 -0.014958796733419988
		 33 -0.015255284839039984 34 -0.014055750488970509 35 -0.01485076066621982 36 -0.017602822514531102
		 37 -0.018996275920496797 38 -0.019677520843192908 39 -0.021027750066525963 40 -0.021836729165251645
		 41 -0.021637232730789657 42 -0.021472329576545379 43 -0.02171243653389382 44 -0.022669362962262851
		 45 -0.024356537773023601 46 -0.023964037716229181 47 -0.02388589188091067 48 -0.022580206357588395
		 49 -0.021648419859297108 50 -0.021855809825553407 51 -0.02157821953215433 52 -0.023604347999242103
		 53 -0.025139885972758458 54 -0.027045960158581073 55 -0.028289310525859035 56 -0.026700960669901075
		 57 -0.024426472542800559 58 -0.022421219511952917 59 -0.023383071749321638 60 -0.023599693595505344
		 61 -0.025656922478647537 62 -0.027057874729393916 63 -0.029297191658824884 64 -0.030991322252144571
		 65 -0.031490119903031966 66 -0.030336808753714029 67 -0.030969861322022896 68 -0.032664465142001387
		 69 -0.033227620935116386 70 -0.033627991782875455 71 -0.034409951619159218 72 -0.035485745123590817
		 73 -0.035695514070143208 74 -0.034995385311520966 75 -0.034403633764404418 76 -0.035454283666770225
		 77 -0.036794078908883754 78 -0.037023084846865228 79 -0.037975133922125315 80 -0.040611479694035946
		 81 -0.041929410614881091 82 -0.043952069244183656 83 -0.045282823963113228 84 -0.045089782579334825;
createNode animCurveTU -n "marker_03_MKR_enable";
	rename -uid "2289E749-4720-8A98-B54E-9798D49D9D62";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 72 ".ktv[0:71]"  14 0 15 1 16 1 17 1 18 1 19 1 20 1 21 1
		 22 1 23 1 24 1 25 1 26 1 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1
		 39 1 40 1 41 1 42 1 43 1 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1
		 56 1 57 1 58 1 59 1 60 1 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1
		 73 1 74 1 75 1 76 1 77 1 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 0;
createNode animCurveTU -n "marker_03_MKR_weight";
	rename -uid "ABC508B0-42F0-E027-1726-CA9A6B976A28";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 70 ".ktv[0:69]"  15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1
		 23 1 24 1 25 1 26 1 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1
		 40 1 41 1 42 1 43 1 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1
		 57 1 58 1 59 1 60 1 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1
		 74 1 75 1 76 1 77 1 78 1 79 1 80 1 81 1 82 1 83 1 84 1;
createNode animCurveTL -n "marker_04_MKR_translateX";
	rename -uid "EFC5FD71-4549-3F99-0CEA-9288B325F7EC";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 90 ".ktv[0:89]"  5 -0.34479667854307017 6 -0.33966803906180332
		 7 -0.33439662921936153 8 -0.32904279442791973 9 -0.32411695152840081 10 -0.31880151174147309
		 11 -0.31253552623009551 12 -0.30714671926148807 13 -0.30097820992426649 14 -0.29666103793378917
		 15 -0.29079506899987084 16 -0.28518797262759171 17 -0.28001517924109071 18 -0.27555433139939928
		 19 -0.27068073717443292 20 -0.26567049380624874 21 -0.26002322080863083 22 -0.25548745752270841
		 23 -0.25066181032983637 24 -0.24506475431432112 25 -0.239445510094008 26 -0.23545572802701115
		 27 -0.23042466611674783 28 -0.22470232479644481 29 -0.21984836043355677 30 -0.21460628352088096
		 31 -0.20933106354785974 32 -0.20513962130173991 33 -0.19989384964338763 34 -0.19482891421026538
		 35 -0.1906558547758691 36 -0.18543686071542126 37 -0.18024634622909225 38 -0.17593123933245225
		 39 -0.17237581967653032 40 -0.16905886246850976 41 -0.16649582888481834 42 -0.16306908480804438
		 43 -0.15918172675392245 44 -0.15606593727663853 45 -0.15220004971061096 46 -0.14850692346865063
		 47 -0.14550715123168123 48 -0.14257035141086161 49 -0.13970678989477348 50 -0.13850179047021405
		 51 -0.13634208853950963 52 -0.1375773233042048 53 -0.14207982913627137 54 -0.14792084569128677
		 55 -0.15369902962409165 56 -0.15937901105699942 57 -0.16476533456344289 58 -0.17116184731368089
		 59 -0.17791475162501375 60 -0.18415438960131969 61 -0.1903611865084236 62 -0.19615720314756807
		 63 -0.20233824095953412 64 -0.20885610065989396 65 -0.21431001716028669 66 -0.22091898284857087
		 67 -0.22716296401391362 68 -0.23342094202520908 69 -0.23919460538359621 70 -0.24652805053293303
		 71 -0.25441023256631068 72 -0.26021458356610383 73 -0.2668632712648491 74 -0.27435117705247236
		 75 -0.28239425644557442 76 -0.28879179965867907 77 -0.29644765363787662 78 -0.30396404395061849
		 79 -0.31133107244361879 80 -0.31831591129388737 81 -0.32449797422457782 82 -0.33108552534954983
		 83 -0.33829585368984794 84 -0.34524316158248092 85 -0.35143767167717682 86 -0.35954030194906894
		 87 -0.36672301472945734 88 -0.37375259872895628 89 -0.38102868547578517 90 -0.38829545030478013
		 91 -0.39506675205093233 92 -0.40332622903004334 93 -0.41159251147086839 94 -0.41939228606537737;
createNode animCurveTL -n "marker_04_MKR_translateY";
	rename -uid "34CBF08D-4E46-0704-7553-87800D092313";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 90 ".ktv[0:89]"  5 -0.14473092410828331 6 -0.14567678651342625
		 7 -0.14543105647203541 8 -0.14609097073403327 9 -0.14629788370448599 10 -0.14700114565710287
		 11 -0.14678859183137799 12 -0.14615076849077541 13 -0.14516262133101154 14 -0.1443452454006669
		 15 -0.14321573205563592 16 -0.14301523615732137 17 -0.14269580462213854 18 -0.14298680033490208
		 19 -0.14367146831409194 20 -0.14413496177504365 21 -0.14423196601307231 22 -0.1446090461830577
		 23 -0.14446658250670669 24 -0.14544484113339029 25 -0.14585284637952084 26 -0.14695441504591367
		 27 -0.14906802558502269 28 -0.1496240039735684 29 -0.14868666933045022 30 -0.14764562286544375
		 31 -0.14731851310274841 32 -0.14727498812388129 33 -0.1474032324276025 34 -0.14579099800420559
		 35 -0.14644953017419071 36 -0.14905697123204775 37 -0.15030339082749955 38 -0.15079721990804279
		 39 -0.1518539804463151 40 -0.15251291532687844 41 -0.15241097977463935 42 -0.15221599350945397
		 43 -0.15213875576091673 44 -0.15308756138437735 45 -0.1545995306769592 46 -0.15408908690337914
		 47 -0.15396874834626312 48 -0.15241510776998679 49 -0.15132733560744499 50 -0.15140213392399487
		 51 -0.1509396138656362 52 -0.15267530997945139 53 -0.15409475966799652 54 -0.15591306973296692
		 55 -0.15707905952855061 56 -0.15539953694389191 57 -0.15303782219809864 58 -0.15104194419034506
		 59 -0.15201962223523885 60 -0.15222940224975734 61 -0.15422752383168331 62 -0.15566399263319042
		 63 -0.15789552301940296 64 -0.15964769493010317 65 -0.16014747809830931 66 -0.15899764173803566
		 67 -0.15961217912186204 68 -0.16130672214353942 69 -0.16186059924435348 70 -0.16223987752311531
		 71 -0.16309425984204845 72 -0.16409628638297841 73 -0.16424881742150471 74 -0.16356110946462438
		 75 -0.16301041892557838 76 -0.16402530123690012 77 -0.16534290780735833 78 -0.16567617783811778
		 79 -0.16672255936239905 80 -0.16941257135407928 81 -0.17077464353083571 82 -0.17287205111620002
		 83 -0.17413050995538404 84 -0.1739041073936532 85 -0.1730478231468926 86 -0.17296924865590302
		 87 -0.17492979758481492 88 -0.17692516125652769 89 -0.17848766985865921 90 -0.1788373528425074
		 91 -0.17801961342366701 92 -0.17883933754458864 93 -0.18183403087358507 94 -0.18553538990860441;
createNode animCurveTU -n "marker_04_MKR_enable";
	rename -uid "EE09EECF-4343-32D2-31E5-9FB4F7940DA8";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 91 ".ktv[0:90]"  4 0 5 1 6 1 7 1 8 1 9 1 10 1 11 1 12 1 13 1
		 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1 27 1 28 1 29 1 30 1
		 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1 44 1 45 1 46 1 47 1
		 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1 61 1 62 1 63 1 64 1
		 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1 79 1 80 1 81 1
		 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1;
createNode animCurveTU -n "marker_04_MKR_weight";
	rename -uid "A50E3545-4447-2AFA-9160-4C81174C7CA7";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 90 ".ktv[0:89]"  5 1 6 1 7 1 8 1 9 1 10 1 11 1 12 1 13 1
		 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1 27 1 28 1 29 1 30 1
		 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1 44 1 45 1 46 1 47 1
		 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1 61 1 62 1 63 1 64 1
		 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1 79 1 80 1 81 1
		 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1;
createNode animCurveTL -n "marker_05_MKR_translateX";
	rename -uid "52183C73-4D7C-7EA8-604A-28BB4D01B2CD";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 0.11115048566092867 1 0.1153411893312043
		 2 0.12101745610984138 3 0.12826333594097361 4 0.1361287472646866 5 0.14599325836081622
		 6 0.15595570281399029 7 0.16628262563358409 8 0.17662467460940257 9 0.18636838179398996
		 10 0.19622711104540913 11 0.20691924475865786 12 0.21663853503917885 13 0.22691045869130955
		 14 0.23531792629545556 15 0.24544304385944604 16 0.25515724225853187 17 0.26431364153017634
		 18 0.27269568984977743 19 0.28115374063347576 20 0.28982869842645909 21 0.2989962139632566
		 22 0.30691237261463455 23 0.31511296635056374 24 0.32352810893766726 25 0.33200204106511189
		 26 0.3383316230855915 27 0.34558759501286596 28 0.35347723026135347 29 0.36051248694900118
		 30 0.36790073696714565 31 0.37510094981682751 32 0.38094231755534014 33 0.38791218406972239
		 34 0.39452157884119343 35 0.39977189073925512 36 0.4059477006580986 37 0.41203009899384069
		 38 0.41702386511572598 39 0.42089003979925788 40 0.42450839639529181 41 0.42736598576402085
		 42 0.43106866862249493 43 0.43490035369509494 44 0.43771678253196067 45 0.44137239005686846
		 46 0.44480538829657024 47 0.44738494588490918 48 0.4498468480381328 49 0.45219617907500986
		 50 0.45242750187470426 51 0.45367701650488546 52 0.45075863257589377 53 0.44460403388976655
		 54 0.43677294902390851 55 0.42904563137468155 56 0.4217625865123088 57 0.41462475332806858
		 58 0.40648660926534497 59 0.39773200807495046 60 0.38954130926897368 61 0.38114234509016842
		 62 0.37329135006395298 63 0.36506570430134599 64 0.3567769831644263 65 0.34949800426718303
		 66 0.34104873714856299 67 0.33274270954223839 68 0.324398121927997 69 0.31656131328970027
		 70 0.30716593264022174 71 0.2971937666508091 72 0.28934041960683932 73 0.28078783484781933
		 74 0.27135131350582364 75 0.26112490506133523 76 0.25251368038069177 77 0.24237414318294181
		 78 0.23253516025310128 79 0.22291836407945442 80 0.21346415756221393 81 0.20509883981414123
		 82 0.19626096579165386 83 0.18667338716906434 84 0.17740222230228775 85 0.16877848337325152
		 86 0.15835970854071735 87 0.14861303718601271 88 0.13905682118062535 89 0.12923801428143011
		 90 0.11943604839542998 91 0.1099392208941784 92 0.099093285161725331 93 0.088142475878298154
		 94 0.077645727660258235;
createNode animCurveTL -n "marker_05_MKR_translateY";
	rename -uid "391BC26D-4121-1206-DBF6-A0A62A1C926C";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 -0.25936185040253856 1 -0.25804740982713031
		 2 -0.25655267293514616 3 -0.25313924857364678 4 -0.25086825713560068 5 -0.24994164304097871
		 6 -0.24960051405315409 7 -0.24788904608487755 8 -0.24694786150723913 9 -0.24571152231294174
		 10 -0.24564290244730441 11 -0.24466002577270241 12 -0.24277304255798243 13 -0.24095353900685418
		 14 -0.23862534172070915 15 -0.23660865045559726 16 -0.23603600669342861 17 -0.23470802808963476
		 18 -0.2335324436922685 19 -0.23271487355697468 20 -0.23091460091205879 21 -0.22913727159438524
		 22 -0.22687719916083837 23 -0.22439055340976638 24 -0.22274857148502658 25 -0.22108058516930634
		 26 -0.21921542542255196 27 -0.21838640921010316 28 -0.21692861066143743 29 -0.2133538536253653
		 30 -0.21009571781181824 31 -0.20836050036925663 32 -0.20649391311617549 33 -0.20498284271220196
		 34 -0.20252513305931386 35 -0.20141605695591036 36 -0.20232469822645499 37 -0.20197465185436053
		 38 -0.20109976867483165 39 -0.20116551743285582 40 -0.20041795267064705 41 -0.19786051506569663
		 42 -0.19573182868694139 43 -0.19434477544239431 44 -0.19292362274013608 45 -0.19275848464715106
		 46 -0.19012845511986504 47 -0.18764741050289629 48 -0.18486091876488536 49 -0.18237994354930892
		 50 -0.18039047143855158 51 -0.17781226040800019 52 -0.17786223638892629 53 -0.17793791490643651
		 54 -0.17799362281505343 55 -0.17674942991349329 56 -0.17378620474793677 57 -0.16989899238064743
		 58 -0.16623103500901615 59 -0.16507419206614327 60 -0.16362940975368895 61 -0.16432070569294466
		 62 -0.16366497690763893 63 -0.16446479369995681 64 -0.16371512561784313 65 -0.16202506582044351
		 66 -0.15881533480133664 67 -0.15735024713233436 68 -0.15690785073259939 69 -0.15513385992295836
		 70 -0.15305432421515897 71 -0.15172423593621354 72 -0.15082412334115691 73 -0.14875259419277304
		 74 -0.14615736182365574 75 -0.14372972377142951 76 -0.14293036625017974 77 -0.14198335624423686
		 78 -0.14058806331726148 79 -0.13990828950609702 80 -0.1407911938455535 81 -0.14052198967159391
		 82 -0.14076216590266377 83 -0.13957155352116923 84 -0.13754495899420216 85 -0.13523002230765407
		 86 -0.13299874661778771 87 -0.13304047836806515 88 -0.13317576082878901 89 -0.13260337927843474
		 90 -0.13074222117703566 91 -0.12793983438152129 92 -0.12694523452521866 93 -0.1277841002879993
		 94 -0.12923899440430148;
createNode animCurveTU -n "marker_05_MKR_enable";
	rename -uid "CCF4A3D5-4F3C-349D-C7D0-FBABA8AF511F";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 1 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1;
createNode animCurveTU -n "marker_05_MKR_weight";
	rename -uid "66F1B330-43C4-FB68-9AF3-58B99A9B88CB";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 1 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1;
createNode animCurveTL -n "marker_06_MKR_translateX";
	rename -uid "F0655E7A-4EC0-03DA-7CE7-76919A553CE6";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 0.27264222727232945 1 0.27536256222050148
		 2 0.27904849022550537 3 0.28355021957597348 4 0.28813082005287149 5 0.29392717766235066
		 6 0.29969355876945225 7 0.3056903414915676 8 0.31147901431944669 9 0.31666002663112447
		 10 0.32223319673650186 11 0.32875873805740807 12 0.33428953769867775 13 0.34049701679430844
		 14 0.3448679050731186 15 0.35065362783452736 16 0.35583062338557658 17 0.36057647744854882
		 18 0.36440950912330283 19 0.36850560506306906 20 0.37273680858502556 21 0.37744057779219753
		 22 0.38084546952065723 23 0.38446086475201702 24 0.38856713978636126 25 0.3928710827941142
		 26 0.39519085699021483 27 0.39855852393223645 28 0.40262165848499099 29 0.40575756762649084
		 30 0.40911928575055179 31 0.41226794081108298 32 0.4141678801567541 33 0.41721009819858856
		 34 0.41993596172015968 35 0.42145599315130422 36 0.42393379745231008 37 0.42658319732316852
		 38 0.42820678421065062 39 0.42883371819131577 40 0.42929940784730791 41 0.42901829562799687
		 42 0.42966566202123835 43 0.43037547029570922 44 0.43020751787723999 45 0.43084813388931775
		 46 0.43144283222617175 47 0.43109480062338867 48 0.43085303384129647 49 0.43045723002566272
		 50 0.42803603425635972 51 0.42664015441894054 52 0.42103283433582772 53 0.41232541536154832
		 54 0.40202712788674022 55 0.39173467911479887 56 0.38195696742753005 57 0.37237842999961057
		 58 0.36175583343112239 59 0.35071090237375879 60 0.34025218529372714 61 0.32961949846023375
		 62 0.31963115397572195 63 0.30937345460844357 64 0.29910812707860457 65 0.28991579952686775
		 66 0.2795812595303877 67 0.2694148589324229 68 0.25911400682222296 69 0.24921316511585212
		 70 0.23790089497206446 71 0.22621358864148389 72 0.2165551245580648 73 0.20620562889421368
		 74 0.19496023628297665 75 0.18288731800261626 76 0.17236566828229027 77 0.16022892346146989
		 78 0.14854333983472479 79 0.13705403889760381 80 0.12591196986075215 81 0.11581254677837172
		 82 0.10517696997850934 83 0.093843691158742915 84 0.082710011555449769 85 0.072294110956954483
		 86 0.060096513246191141 87 0.048580653295214327 88 0.037213039562104311 89 0.025589272353823356
		 90 0.01397004007245517 91 0.0025711487007582523 92 -0.010043138165133858 93 -0.022795557623610463
		 94 -0.034971465059671247;
createNode animCurveTL -n "marker_06_MKR_translateY";
	rename -uid "4A0BB303-432A-BBB3-BF1D-B6AE72DAFA3F";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 -0.18447243832928079 1 -0.18328584561147898
		 2 -0.18182421415971178 3 -0.17853649078837253 4 -0.17651849288279592 5 -0.17583681934585604
		 6 -0.17585553343020283 7 -0.17442112301267265 8 -0.17381931072181356 9 -0.173053826403268
		 10 -0.17351904682115377 11 -0.17295829228719295 12 -0.1715288723472001 13 -0.17026783423028996
		 14 -0.16825623831852632 15 -0.16686168305240368 16 -0.1669580332650713 17 -0.16606049316698868
		 18 -0.16530938692497676 19 -0.16500346947709005 20 -0.1635096873366173 21 -0.16219151845640284
		 22 -0.16038637225074182 23 -0.15835206747051017 24 -0.15712914221165841 25 -0.15596492172232373
		 26 -0.15445652397586412 27 -0.15403611775697801 28 -0.15309109414498406 29 -0.15003506304813313
		 30 -0.14734680013795254 31 -0.1462472077868604 32 -0.14494220327847251 33 -0.14402443408126253
		 34 -0.14220006105216126 35 -0.14168885926591812 36 -0.14317447939952521 37 -0.14331955331219426
		 38 -0.1430137673015015 39 -0.14364750022089101 40 -0.14344318532663097 41 -0.14141659794806055
		 42 -0.13985357891083106 43 -0.13904476113780001 44 -0.13821731127008019 45 -0.13865776335125596
		 46 -0.13657447161313685 47 -0.13469333794923249 48 -0.13245332155317785 49 -0.1304737789233556
		 50 -0.12911840160053312 51 -0.12714696369195816 52 -0.12789432197334472 53 -0.1285584117687727
		 54 -0.12928557435300991 55 -0.12876889720171913 56 -0.12641225760110042 57 -0.12313119714729071
		 58 -0.12009635375186073 59 -0.11959205938944539 60 -0.11874654046053551 61 -0.12002482815355314
		 62 -0.12000406439796912 63 -0.12136922618275997 64 -0.12119381669325485 65 -0.12014517227793597
		 66 -0.11754468116072853 67 -0.11668304822475034 68 -0.11685268849321212 69 -0.11568547146461206
		 70 -0.11427595785683614 71 -0.11352540012960222 72 -0.11316825369830935 73 -0.11172146641480535
		 74 -0.109682469739878 75 -0.10780275245120635 76 -0.10758192510168135 77 -0.10728151583562123
		 78 -0.10644413603094355 79 -0.10625620650413287 80 -0.10767549300588714 81 -0.10792211741553781
		 82 -0.10865209282490634 83 -0.10805665580573526 84 -0.10656448187345358 85 -0.10467119175309031
		 86 -0.10299754837117642 87 -0.10355664346230387 88 -0.10421352154466201 89 -0.10420410593346541
		 90 -0.10290863937685923 91 -0.1006233165457569 92 -0.10010442096668787 93 -0.10146055950731309
		 94 -0.10351596193240381;
createNode animCurveTU -n "marker_06_MKR_enable";
	rename -uid "9968067A-4F7F-BDC7-9922-4C93D47BABD6";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 1 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1;
createNode animCurveTU -n "marker_06_MKR_weight";
	rename -uid "A9C95ABA-4CD8-0012-91E4-419368868EB6";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 1 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1;
createNode animCurveTL -n "marker_07_MKR_translateX";
	rename -uid "844914C8-489F-40EF-532F-4D8F816E8E0B";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 0.41492777558317084 1 0.41603612670447943
		 2 0.4171212681908042 3 0.41833109471061691 4 0.41922194729835494 5 0.42040506944196554
		 6 0.42122283897215773 7 0.4218786391122552 8 0.42220728024712983 9 0.42221353869011535
		 10 0.4227985897259755 11 0.42459479154874058 12 0.42513574539520649 13 0.42664713708485924
		 14 0.42616527520326852 15 0.42706273320713073 16 0.42754849180416787 17 0.42747421925505968
		 18 0.42621592346355086 19 0.42520563813353796 20 0.42412435826976835 21 0.42362682148479214
		 22 0.42149452203267734 23 0.41991865793129923 24 0.41880954081265576 25 0.41805168978088236
		 26 0.41552553675894699 27 0.41404299489657559 28 0.41350652331666682 29 0.41194088857007649
		 30 0.41054084524885182 31 0.40908574911589457 32 0.40640938580340458 33 0.40485273822863044
		 34 0.40331525733860674 35 0.40035903727532762 36 0.39850413596365231 37 0.39703887774627489
		 38 0.39480751349328569 39 0.39168025201451029 40 0.38839727376090716 41 0.38434443560831366
		 42 0.38120590776587759 43 0.37830462521850128 44 0.37433933807019637 45 0.3713679124693775
		 46 0.36837267100904647 47 0.36443532182889216 48 0.36086204064963634 49 0.35726067192574951
		 50 0.35151692832890058 51 0.34673732246904709 52 0.33796273539744981 53 0.32626578747365309
		 54 0.3130453400122527 55 0.2996264978731723 56 0.28689313500263924 57 0.27436563715608209
		 58 0.26082311964211413 59 0.24682477614952281 60 0.23350011030760687 61 0.2201412539908304
		 62 0.20724247683542085 63 0.19428464357255992 64 0.18136998185330888 65 0.16941908165228181
		 66 0.15646795560380555 67 0.14346510689135128 68 0.1303556120679269 69 0.11752079508782365
		 70 0.10336764737672022 71 0.088925785475795771 72 0.076612559939543967 73 0.063461075873207151
		 74 0.049456539920398779 75 0.03455437027563113 76 0.020985079769972437 77 0.0056939350692529755
		 78 -0.0090520596234511808 79 -0.023470976724415338 80 -0.037554113436161218 81 -0.050603083026294848
		 82 -0.064197240131430355 83 -0.078676105293701559 84 -0.092927782595163932 85 -0.10644215883799091
		 86 -0.12197782174902444 87 -0.13679634870354407 88 -0.15137923523417007 89 -0.16646210926947863
		 90 -0.18178402249604464 91 -0.19668472993738195 92 -0.21283290148157774 93 -0.22917284514741693
		 94 -0.24491763243480824;
createNode animCurveTL -n "marker_07_MKR_translateY";
	rename -uid "6B8402FB-41B0-5EB8-8FFC-ED99999449CD";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 0.24102884665430102 1 0.24175376847079444
		 2 0.24261055640388984 3 0.24490499181108238 4 0.24568566575634432 5 0.24475834997233181
		 6 0.24304026917482591 7 0.24273588699462079 8 0.24136037347562167 9 0.24017725164331993
		 10 0.23769496011784153 11 0.23648707720862594 12 0.23607083025264519 13 0.23557036731087466
		 14 0.23576788599395648 15 0.23526816479662904 16 0.23325745387044394 17 0.23221576070704353
		 18 0.23088069306852499 19 0.2290565951952328 20 0.22854972983449051 21 0.22778353726134493
		 22 0.22735132779986134 23 0.22742937001692143 24 0.22649163226357871 25 0.22568644645903746
		 26 0.22496680374297062 27 0.22344501357098068 28 0.22253811554518987 29 0.22344634490756066
		 30 0.22418955280575492 31 0.2231321301070468 32 0.22217583646247863 33 0.22096371754590738
		 34 0.22074898988281666 35 0.21911519769137022 36 0.2154853365361179 37 0.21340918316243074
		 38 0.21188059512048285 39 0.20926426914020047 40 0.20753974769411909 41 0.20758476151950167
		 42 0.20728458463738153 43 0.20614297055521469 44 0.20479446591250594 45 0.20253685565343826
		 46 0.20271541556959338 47 0.20263325097521057 48 0.2030751514203557 49 0.20332646950450017
		 50 0.20268673194534581 51 0.20269742051381223 52 0.19973566449162328 53 0.19683608362288163
		 54 0.19374331142595291 55 0.19195736288647214 56 0.19218229591616975 57 0.19357721698721042
		 58 0.19468100349912887 59 0.19320093055748633 60 0.19213755811478128 61 0.18893727139589334
		 62 0.18711468913437024 63 0.1841611497997665 64 0.18247602592486856 65 0.18195746253295197
		 66 0.18303594946716595 67 0.1824837640727891 68 0.1807846087805105 69 0.18047341850603138
		 70 0.18018882217435184 71 0.17959030960903843 72 0.17872290643644262 73 0.17889486959481582
		 74 0.17978527643251019 75 0.18043855253091956 76 0.17959890262511946 77 0.17874831698321969
		 78 0.17872556696265696 79 0.17805756243620474 80 0.17574968506096089 81 0.17486312525708891
		 82 0.17330040050626205 83 0.17311192922888141 84 0.17398989542973153 85 0.17546740140684269
		 86 0.17668216506708567 87 0.17555646331884145 88 0.174447826683373 89 0.17399330812272651
		 90 0.17493098662167661 91 0.17705800364470159 92 0.1776884982677982 93 0.17611823990909026
		 94 0.17382255884693298;
createNode animCurveTU -n "marker_07_MKR_enable";
	rename -uid "4B1B1779-490C-9DA4-826D-909FACC8A850";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 1 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1;
createNode animCurveTU -n "marker_07_MKR_weight";
	rename -uid "8953D530-458B-AD9D-0207-0EA6D06E6546";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 95 ".ktv[0:94]"  0 1 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1;
createNode animCurveTL -n "marker_08_MKR_translateX";
	rename -uid "00A5B05B-412E-02F2-B0C9-8EAB38619435";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 73 ".ktv[0:72]"  0 -0.1510288448141493 1 -0.15032413356308189
		 2 -0.14969076963478617 3 -0.14914486122392873 4 -0.14896151407204972 5 -0.14827345819651011
		 6 -0.14790977217221585 7 -0.14777426813287098 8 -0.1478472150203376 9 -0.1481771589066444
		 10 -0.14801448970629583 11 -0.1466314034414522 12 -0.14652946824618229 13 -0.14550478198731392
		 14 -0.14631067815896154 15 -0.14574440773548919 16 -0.14556618435158003 17 -0.14575884751424029
		 18 -0.14703749141296252 19 -0.14808790654277471 20 -0.1491237152095084 21 -0.14970192459584591
		 22 -0.15161032831408439 23 -0.15315941578316716 24 -0.15406137297768435 25 -0.15466622129684593
		 26 -0.15679621803305027 27 -0.15792620863119972 28 -0.15828287132194829 29 -0.15967764280468982
		 30 -0.16084255950902437 31 -0.16197415334246629 32 -0.16421834130687712 33 -0.16540348874789784
		 34 -0.16675371630832325 35 -0.16901858728908159 36 -0.17018765467840746 37 -0.17123751264843279
		 38 -0.17295713874272894 39 -0.17534086086829415 40 -0.17795773092650541 41 -0.18151721602900855
		 42 -0.18408636310004506 43 -0.18633889360293687 44 -0.18948708942041276 45 -0.19171664654719989
		 46 -0.1941522471375412 47 -0.19740033853527311 48 -0.2004647915955064 49 -0.20352967579351622
		 50 -0.20855027788864405 51 -0.21259847659485037 52 -0.2204333364667399 53 -0.23114410785235329
		 54 -0.2434934061007536 55 -0.2561137150793053 56 -0.26841620359430574 57 -0.28072913474361227
		 58 -0.29410275168463718 59 -0.30787324159264073 60 -0.32108834724596225 61 -0.33420034557091122
		 62 -0.34713652836083214 63 -0.36011218167911491 64 -0.37345657638958329 65 -0.38579715663103853
		 66 -0.39939736657448394 67 -0.41307161476183457 68 -0.42698236175634718 69 -0.44070971318576968
		 70 -0.45599974117966019 71 -0.47167172850814648 72 -0.48522191360421224;
createNode animCurveTL -n "marker_08_MKR_translateY";
	rename -uid "CB428583-4252-562B-BD8A-B084D49DAD47";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 73 ".ktv[0:72]"  0 0.22154590140954167 1 0.22247022238502601
		 2 0.22321544314907449 3 0.22579362176797546 4 0.22728856281314536 5 0.22689341461308277
		 6 0.22570030037740096 7 0.22584190578127405 8 0.22498654193731149 9 0.22450214964636095
		 10 0.22344574820136776 11 0.2232709153797936 12 0.22369835264006288 13 0.22437090159030315
		 14 0.22514504382151068 15 0.22586666956433921 16 0.22565641245181423 17 0.22561600427747641
		 18 0.2251464569065037 19 0.22430463718648985 20 0.22372274646501566 21 0.22351941027172506
		 22 0.22300312289095647 23 0.22305884744842674 24 0.22186658311185037 25 0.22124740588322267
		 26 0.22001712337603907 27 0.21777781509023364 28 0.21694286134723118 29 0.21770716563204839
		 30 0.21840220670318122 31 0.21835741101918527 32 0.2180737545655822 33 0.21755202336269996
		 34 0.21898641077587222 35 0.21790253915785063 36 0.2149113708957493 37 0.21341749753599393
		 38 0.21259632979487109 39 0.21126688825844298 40 0.21035495394553716 41 0.21029724873264632
		 42 0.21029616292244513 43 0.2100155433828268 44 0.20864247852817441 45 0.20679278909642496
		 46 0.20699301396859271 47 0.20678311472903554 48 0.20814421374743919 49 0.20899521777023411
		 50 0.20872011669035573 51 0.20884157728010555 52 0.20699922210109079 53 0.20577599563844284
		 54 0.20417036640151354 55 0.20317755470341348 56 0.2053977908872191 57 0.20828862384359714
		 58 0.21093328053240767 59 0.21046795792489181 60 0.21091707886638411 61 0.20958490051941103
		 62 0.20872307069061635 63 0.20723772103980698 64 0.2061759042025384 65 0.20618897765633493
		 66 0.20807028536046623 67 0.20821094032910004 68 0.20748174626896521 69 0.20774714659766569
		 70 0.20823202130991003 71 0.20842558470703632 72 0.20836549747264832;
createNode animCurveTU -n "marker_08_MKR_enable";
	rename -uid "4186305C-47DF-5E16-EDAC-B0A20EAA73B0";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 74 ".ktv[0:73]"  0 1 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 0;
createNode animCurveTU -n "marker_08_MKR_weight";
	rename -uid "A3A98C4A-46E4-5529-9A9D-068ECCD4E380";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 73 ".ktv[0:72]"  0 1 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1;
createNode animCurveTL -n "marker_09_MKR_translateX";
	rename -uid "45B1038C-46A2-39D4-38DF-71B2C00D2A86";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 41 ".ktv[0:40]"  54 0.48380024250737519 55 0.46906894303869739
		 56 0.45523072704951995 57 0.441554149660488 58 0.42698931100131421 59 0.41189000500671447
		 60 0.3975212183119522 61 0.38317369659758271 62 0.36928934463237439 63 0.35542546566588962
		 64 0.34168369671601029 65 0.3290131598791538 66 0.31541783115758981 67 0.30165662899916812
		 68 0.28782664313860595 69 0.27438839432639095 70 0.25960787806408048 71 0.24461482486056174
		 72 0.23175121841044888 73 0.21816028614553373 74 0.20375191446000385 75 0.18838013619726457
		 76 0.174377968935854 77 0.15873750926274721 78 0.14367547016561377 79 0.12898915558558122
		 80 0.11458742709365655 81 0.10128948256380554 82 0.08748181928645915 83 0.072864646829284729
		 84 0.058526729980499903 85 0.0449481881302497 86 0.029442014678870865 87 0.014578685471865582
		 88 -3.0510052630272622e-05 89 -0.015034237496894476 90 -0.030194257037788885 91 -0.044955980304073384
		 92 -0.060884386170979521 93 -0.076989555411815291 94 -0.09251793901384503;
createNode animCurveTL -n "marker_09_MKR_translateY";
	rename -uid "D63102A4-4F2E-6D42-6686-37BAF37D83B1";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 41 ".ktv[0:40]"  54 0.21900151440599946 55 0.21661662136913351
		 56 0.21622631571555007 57 0.21683648578445169 58 0.21735719744506832 59 0.21529973574676331
		 60 0.21364111518628082 61 0.20986333244631061 62 0.20762646960934861 63 0.20412763912890586
		 64 0.20233275926606653 65 0.20156912324567278 66 0.20241432200804266 67 0.20144910989903397
		 68 0.19938785078049326 69 0.1988094289323985 70 0.19856103547787296 71 0.19768535010743482
		 72 0.19638389679696355 73 0.19653335143242501 74 0.19710341016697375 75 0.19744377998081675
		 76 0.19625079285547287 77 0.19523835771755926 78 0.19470812961296957 79 0.19378119614696132
		 80 0.19112745722766389 81 0.18996976388026954 82 0.18815477907572242 83 0.18784811383872857
		 84 0.18846890019027185 85 0.18964801397407083 86 0.19044016159478783 87 0.18907077676453166
		 88 0.18771130689436755 89 0.18713963918030974 90 0.1878406214078665 91 0.18968057389367232
		 92 0.18986841558443002 93 0.18812975841843349 94 0.18571218472802742;
createNode animCurveTU -n "marker_09_MKR_enable";
	rename -uid "E2EBC655-4396-6A9C-6CCD-BEA7A42DEAA2";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 42 ".ktv[0:41]"  53 0 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1;
createNode animCurveTU -n "marker_09_MKR_weight";
	rename -uid "001952E5-449A-9852-F95C-C49AF5420CFF";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 41 ".ktv[0:40]"  54 1 55 1 56 1 57 1 58 1 59 1 60 1 61 1
		 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1
		 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1;
createNode animCurveTL -n "marker_10_MKR_translateX";
	rename -uid "9DD96876-44C1-AABE-C155-77B86032DA53";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 67 ".ktv[0:66]"  0 0.38751676528094714 1 0.38882057827380812
		 2 0.39034284063562019 3 0.39192255669613374 4 0.39323757343228694 5 0.39525492558299002
		 6 0.39681513730296714 7 0.39837825503520086 8 0.39975661402801155 9 0.40058797610633945
		 10 0.40170198530828538 11 0.40410163549891354 12 0.40540073368656049 13 0.4073256634282636
		 14 0.40770451420705078 15 0.40909577503862837 16 0.40990605463741669 17 0.41042659086845079
		 18 0.40997036096204753 19 0.40981887811188922 20 0.40997600243648746 21 0.41039728434176115
		 22 0.40957418125071987 23 0.40915362966722069 24 0.40937786470232729 25 0.40966029952240235
		 26 0.4085682968959008 27 0.40850785330764072 28 0.40891630956125136 29 0.40855893628439854
		 30 0.40807291199370599 31 0.40733234752352476 32 0.40546222538954957 33 0.40469274497328456
		 34 0.40353856287562584 35 0.40152932985919232 36 0.40058426391674584 37 0.39992423206522987
		 38 0.39829465709442169 39 0.39577086081284107 40 0.39313229528198645 41 0.39006376345079508
		 42 0.38769602244517576 43 0.38543582916462726 44 0.38245396298208323 45 0.38025720545186914
		 46 0.37816327796203097 53 0.34078863830911055 54 0.3282111978615202 55 0.3155184396785945
		 56 0.30307850894568711 57 0.29099412959915327 58 0.27783249027266976 59 0.26453790839878399
		 60 0.25170394430096588 61 0.23877032076844984 62 0.22660385927211479 63 0.21408202186520153
		 64 0.20200815792119298 65 0.19083716823835806 66 0.17853370880064301 67 0.16627229347766548
		 68 0.15390898461836233 69 0.14186661148879776 70 0.12855805402092257 71 0.11486715817847737
		 72 0.10325989801201618;
createNode animCurveTL -n "marker_10_MKR_translateY";
	rename -uid "25C3ACA7-4B3A-B267-7228-A0A159943759";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 67 ".ktv[0:66]"  0 -0.3803555308874037 1 -0.37900810317956185
		 2 -0.37720816394076773 3 -0.37361815589770947 4 -0.37121379383608499 5 -0.37001602610304773
		 6 -0.36944026553821246 7 -0.36740026321262376 8 -0.36608606982445518 9 -0.36470469986957588
		 10 -0.36463526662576762 11 -0.36366813209494442 12 -0.36167633481579697 13 -0.35995017705030152
		 14 -0.3572921326828834 15 -0.35532899976740484 16 -0.35491656035466901 17 -0.35343451048260521
		 18 -0.35195450979266291 19 -0.35096243099288582 20 -0.34876685605383062 21 -0.34674671185906636
		 22 -0.34411745205336552 23 -0.34140724349990048 24 -0.33957024227703958 25 -0.33776971823416707
		 26 -0.33554218813034453 27 -0.33451851615603828 28 -0.33303499889216825 29 -0.32940936624733175
		 30 -0.32617071350988824 31 -0.3244819806818845 32 -0.3225550533999082 33 -0.32101605835821201
		 34 -0.31855676306652503 35 -0.31742211058463043 36 -0.31834478411101336 37 -0.3179482397088661
		 38 -0.31702028757277784 39 -0.31706245381950432 40 -0.31623282321004564 41 -0.3136887573068281
		 42 -0.31162280360902422 43 -0.31028730852997277 44 -0.30898811792912351 45 -0.30891493119278668
		 46 -0.30641780444259448 53 -0.29473243391773207 54 -0.2947217430032647 55 -0.29359753116388121
		 56 -0.29054938211384873 57 -0.28667881983209714 58 -0.28299881587684744 59 -0.28199953430038993
		 60 -0.28063238317539169 61 -0.2813423539535993 62 -0.28095436202390267 63 -0.28186280378773515
		 64 -0.28156394628969239 65 -0.28034192522070367 66 -0.27753905649177962 67 -0.27648547014155056
		 68 -0.2765953979748077 69 -0.27537118646279135 70 -0.2738842202908216 71 -0.27315210381517463
		 72 -0.27276227254110019;
createNode animCurveTU -n "marker_10_MKR_enable";
	rename -uid "EE529F9E-4649-3967-258F-7DA783682515";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 74 ".ktv[0:73]"  0 1 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 0 48 0 49 0 50 0 51 0 52 0 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 0;
createNode animCurveTU -n "marker_10_MKR_weight";
	rename -uid "A61C0CD3-4917-99A0-5A3F-B298FDF7C793";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 67 ".ktv[0:66]"  0 1 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1 61 1 62 1 63 1 64 1 65 1 66 1
		 67 1 68 1 69 1 70 1 71 1 72 1;
createNode animCurveTL -n "marker_11_MKR_translateX";
	rename -uid "427B8975-4C2D-C550-E7C8-3A8815096A4B";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 39 ".ktv[0:38]"  52 0.4907366314493723 53 0.47949934229235636
		 54 0.46680520965038452 55 0.45420877130184434 56 0.44179300855458314 57 0.42965964053707328
		 58 0.41671809994120412 59 0.40338786633669277 60 0.39071439472928027 61 0.37794895677870022
		 62 0.3658658831570748 63 0.35359063784751632 64 0.34159338549974594 65 0.33064660646100008
		 66 0.31859941516329304 67 0.30658515231809158 68 0.29446931341002813 69 0.28283765078506451
		 70 0.26978157842136896 71 0.25632019590724886 72 0.24506870615279364 73 0.23314568095992416
		 74 0.22019107454472897 75 0.20636132958823927 76 0.19399984682877602 81 0.12864002478769221
		 82 0.11641987438159129 83 0.10357555937120277 84 0.090766631236405271 85 0.078614777697676108
		 86 0.064795978447182989 87 0.051554464335575312 88 0.038596930620134584 89 0.025275786635708175
		 90 0.011918849242186225 91 -0.0010747056444165848 92 -0.015439427554506557 93 -0.029775530430531771
		 94 -0.043542918465784786;
createNode animCurveTL -n "marker_11_MKR_translateY";
	rename -uid "05DD3FB5-4CE3-6768-04B7-37B2FDEEA15A";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 39 ".ktv[0:38]"  52 -0.3613093813274636 53 -0.36003819366516732
		 54 -0.35866703378334047 55 -0.35608073303667198 56 -0.35188189829376337 57 -0.34672997159128
		 58 -0.34190333119231614 59 -0.33950818852763232 60 -0.33699529241605197 61 -0.33670360979214919
		 62 -0.33500388162173439 63 -0.33492097486398104 64 -0.33332078227238821 65 -0.33096713937577271
		 66 -0.32701778806992715 67 -0.32486907261454273 68 -0.32378118107435067 69 -0.32136676331276148
		 70 -0.31866715474684859 71 -0.31675174376920778 72 -0.31537646811454467 73 -0.31291596703682145
		 74 -0.30991005563738377 75 -0.30705468798185942 76 -0.30595467084558925 81 -0.30222399349252627
		 82 -0.30230420156882021 83 -0.30113278416529721 84 -0.29907183598821951 85 -0.29671629748493433
		 86 -0.2945658717911992 87 -0.29470454346315555 88 -0.2949913737607931 89 -0.29465062842874012
		 90 -0.29306886093952311 91 -0.29055572685762315 92 -0.28979547478118833 93 -0.29101482361746445
		 94 -0.29294502026278113;
createNode animCurveTU -n "marker_11_MKR_enable";
	rename -uid "E4B36B56-4422-BAD9-EE9C-C7AACB52E0C4";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 44 ".ktv[0:43]"  51 0 52 1 53 1 54 1 55 1 56 1 57 1 58 1
		 59 1 60 1 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1
		 76 1 77 0 78 0 79 0 80 0 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1
		 93 1 94 1;
createNode animCurveTU -n "marker_11_MKR_weight";
	rename -uid "771E0468-4648-16F5-A2DE-9CBCFAD7E753";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 39 ".ktv[0:38]"  52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1
		 60 1 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1
		 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1;
createNode animCurveTL -n "marker_12_MKR_translateX";
	rename -uid "19EF28C8-4981-ABB7-DD88-EFB4D32B8D14";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 65 ".ktv[0:64]"  0 -0.37677026795495566 1 -0.37560413042656954
		 2 -0.37422751939600618 3 -0.372868635697853 4 -0.37178052705155362 5 -0.36995943920496338
		 6 -0.36836674277310821 7 -0.36686976700594831 8 -0.36547284880967718 9 -0.36452574976170804
		 10 -0.36318260782645317 11 -0.36072538140914356 12 -0.35934348815343853 13 -0.35701644910172659
		 14 -0.35639798727201233 15 -0.35465645623054309 16 -0.35336657911882163 17 -0.35232332984614034
		 18 -0.35212344266000817 19 -0.35158337284336472 20 -0.35070363681278727 21 -0.34952001131286564
		 22 -0.3493343890695273 23 -0.34887643273170832 24 -0.34762430943554301 25 -0.34630244436375379
		 26 -0.34623726328338622 27 -0.34511353447712267 28 -0.3435436486066637 29 -0.34264881648396905
		 30 -0.34185921228725369 31 -0.34104294502322235 32 -0.34141971239378188 33 -0.34071379488401488
		 34 -0.34021857594306332 35 -0.34060512792061504 36 -0.33988456225085234 37 -0.33887776978310236
		 38 -0.33876216107411422 39 -0.33958187431335929 40 -0.34035385021538733 41 -0.34173558647859714
		 42 -0.34229024327891677 43 -0.34254124484427417 44 -0.34351676530972336 45 -0.34377304412076337
		 46 -0.34393385687553063 47 -0.34486586463131685 48 -0.34600532441060472 49 -0.34706873396118887
		 50 -0.34988696002185743 51 -0.35176034765769471 52 -0.35754491827621959 53 -0.36671669286765496
		 54 -0.37737135929625887 55 -0.38802188547553162 56 -0.39875258039047146 57 -0.40916332393500154
		 58 -0.42071055998092832 59 -0.43259681536277594 60 -0.44408222682154869 61 -0.45576001373010183
		 62 -0.46670042669190326 63 -0.47817442528776949 64 -0.48957062719646122;
createNode animCurveTL -n "marker_12_MKR_translateY";
	rename -uid "F8301C51-4BB5-09B2-7026-9BB0B4BA6801";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 65 ".ktv[0:64]"  0 -0.31776930089644678 1 -0.31693519012950122
		 2 -0.31631953215556519 3 -0.31393270417648728 4 -0.31262018905017175 5 -0.3131301913147676
		 6 -0.31432344260787565 7 -0.31442601997970732 8 -0.31539020642196536 9 -0.31595792478617502
		 10 -0.31693783876084891 11 -0.31698647222262655 12 -0.31666177970129761 13 -0.31584094450736222
		 14 -0.31540709523628441 15 -0.31455509172555213 16 -0.31455399198654566 17 -0.31454313145442403
		 18 -0.31521464639179708 19 -0.31630964108075899 20 -0.31724327644699052 21 -0.31780788590378006
		 22 -0.31882210727402638 23 -0.31926841728308336 24 -0.3209148820377023 25 -0.32185157859269392
		 26 -0.32369979128837134 27 -0.32653598179150539 28 -0.32766136651023547 29 -0.32749182984530989
		 30 -0.32722472883377646 31 -0.32732265865219234 32 -0.3279135030672396 33 -0.32868226699296216
		 34 -0.32746805049808814 35 -0.32876976031440408 36 -0.33194067451718806 37 -0.33383679238440783
		 38 -0.33482274012151614 39 -0.33637219277082275 40 -0.33758523246758299 41 -0.33840082785891357
		 42 -0.33905286417568148 43 -0.33959174224586464 44 -0.34153687843274966 45 -0.34378650085350193
		 46 -0.34422892663970905 47 -0.34517501330887379 48 -0.34437764430920126 49 -0.34407483883316636
		 50 -0.34520532627825717 51 -0.34592256003672461 52 -0.34872682051235326 53 -0.35133799885775918
		 54 -0.35455041773848417 55 -0.35753705627992716 56 -0.35728666471243797 57 -0.3565259061073992
		 58 -0.35626949576149347 59 -0.35926826111030896 60 -0.36134962411610627 61 -0.36504486239544021
		 62 -0.36859492769777258 63 -0.37276897373962103 64 -0.37699205391963092;
createNode animCurveTU -n "marker_12_MKR_enable";
	rename -uid "F94362A2-4FE8-C6C4-157F-8B93E9E87622";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 66 ".ktv[0:65]"  0 1 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 0;
createNode animCurveTU -n "marker_12_MKR_weight";
	rename -uid "A6D710FA-415A-354A-3137-46BB77664B55";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 65 ".ktv[0:64]"  0 1 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1;
createNode animCurveTL -n "marker_13_MKR_translateX";
	rename -uid "0B4B0205-45B9-19FE-FCDF-2FA659D4B8D2";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 89 ".ktv[0:88]"  0 0.065837941512844278 1 0.066688547878951288
		 2 0.067423217454506745 3 0.068208334776439616 4 0.068739169206074813 5 0.069710857038674079
		 6 0.070253127035000196 7 0.070606740368695964 8 0.070792236652300722 9 0.070673990004535781
		 10 0.07125694478738831 11 0.072924292802271307 12 0.073298397796365378 13 0.074686601774073158
		 14 0.074103730421127501 15 0.074961457829287759 16 0.075614388623374995 17 0.075645058000606724
		 18 0.074512206011929427 19 0.073733833968524731 20 0.072677674003859938 21 0.072280295342369349
		 22 0.070292314520311483 23 0.068789621989068461 24 0.067790476406580424 25 0.067162225449843516
		 26 0.064832492866885527 27 0.063491664270099113 28 0.06312139617308421 29 0.061662267078138711
		 30 0.060441028938106101 31 0.059454093665027075 32 0.057234689591446175 33 0.056095322473315723
		 34 0.055005723798643213 35 0.05271019859254833 36 0.051392198571282077 37 0.050343374811162689
		 38 0.048668715447474309 39 0.046314154407635422 40 0.043699169984404374 41 0.040075633453399262
		 42 0.03742192060944094 43 0.035157677107641838 44 0.031760147913488024 45 0.029451826870050768
		 46 0.026863007948731643 47 0.023455992017646476 48 0.02048254291097007 49 0.017401320740257797
		 50 0.012336022212832032 51 0.00816979693430675 52 0.00044176532863360318 53 -0.010029035391705299
		 54 -0.022048799649335649 55 -0.034423828371011322 56 -0.046189889624269231 57 -0.057927352882291394
		 58 -0.070691775201128182 59 -0.083953976432453559 60 -0.096540376197391753 61 -0.10901986377832196
		 62 -0.12134460187723861 63 -0.13366973152720663 64 -0.14628369201298386 65 -0.15802667997139719
		 66 -0.17082239457718079 67 -0.18362491151808952 68 -0.19656626400253996 69 -0.20938715362324395
		 70 -0.22363578237424597 71 -0.23819101589322011 72 -0.2505687466931168 73 -0.26408627279025237
		 74 -0.27845813303878597 75 -0.29374698304356117 76 -0.30776764079994134 77 -0.3236239133946513
		 78 -0.33898105562266523 79 -0.35404445316063521 80 -0.3687462644064099 81 -0.38261615362471391
		 82 -0.39710005180733193 83 -0.4127520929939944 84 -0.42821327901383155 85 -0.44299144541025093
		 86 -0.4601864740290213 87 -0.47647294933309958 88 -0.49263719607700868;
createNode animCurveTL -n "marker_13_MKR_translateY";
	rename -uid "9E8A30E6-4B34-2399-D07E-85BD89317488";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 89 ".ktv[0:88]"  0 0.47492528846975157 1 0.47569782310865005
		 2 0.4764206256698077 3 0.47887448263261945 4 0.4798302700782292 5 0.47892453884845976
		 6 0.47710660471974842 7 0.47671429891627604 8 0.47528478690135334 9 0.4740609726471734
		 10 0.47188111374315778 11 0.47104230521306156 12 0.47079397494294284 13 0.47067574893487985
		 14 0.47085184780886524 15 0.47081767593602741 16 0.46941271762183878 17 0.46863359632512747
		 18 0.46737090961969419 19 0.46566791830972765 20 0.4646491843787024 21 0.46378549551038106
		 22 0.46281050228835074 23 0.46236335869177136 24 0.4607732457332977 25 0.45966967441017947
		 26 0.45822380122443596 27 0.45571779025250225 28 0.45429928500949235 29 0.45476608284737718
		 30 0.45515813508496661 31 0.45423272383463309 32 0.45318792132379504 33 0.45204848289731125
		 34 0.45240449363676316 35 0.45062578393402797 36 0.44686919289297811 37 0.44467862046021667
		 38 0.4430798895682071 39 0.44075372474808283 40 0.43911110545469689 41 0.43868760961878805
		 42 0.43820035906685828 43 0.43718797879040106 44 0.43549960575634383 45 0.43291196026877932
		 46 0.43279314874936237 47 0.43228904995245865 48 0.43301476067388522 49 0.43339228592416046
		 50 0.43258015398378957 51 0.43238830858700561 52 0.42963845510661447 53 0.42740414156730555
		 54 0.42485623410705975 55 0.42323787025902293 56 0.42466195864615164 57 0.4268218898579702
		 58 0.42889167522356619 59 0.42791474677154362 60 0.42772894607724232 61 0.42560447768076171
		 62 0.4243218693246873 63 0.42220919643214971 64 0.42089277708987871 65 0.42092935498332329
		 66 0.42281154411311206 67 0.4227534781210166 68 0.42175964120589593 69 0.42208073605357532
		 70 0.42264716015986314 71 0.42302865768878517 72 0.42289044928251096 73 0.4240928198323296
		 74 0.42624552818411476 75 0.42837370052129542 76 0.42897715809776671 77 0.42952035236804043
		 78 0.43127938477613292 79 0.43232037796273448 80 0.43160537971371582 81 0.43235483682677134
		 82 0.43263215341552719 83 0.43386781041529199 84 0.43683760170363684 85 0.44060309364700001
		 86 0.44399003457219566 87 0.44512002377462512 88 0.44638089177666085;
createNode animCurveTU -n "marker_13_MKR_enable";
	rename -uid "9CBABE0D-4147-C86D-6727-28A1B1064473";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 90 ".ktv[0:89]"  0 1 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 0;
createNode animCurveTU -n "marker_13_MKR_weight";
	rename -uid "C1C66413-46A7-E70C-A3B1-BDBDBA37D31F";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 89 ".ktv[0:88]"  0 1 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1;
createNode animCurveTL -n "marker_14_MKR_translateX";
	rename -uid "542A3CEE-4997-7BC3-38A7-9B8FB770556E";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 36 ".ktv[0:35]"  59 0.48139269071158042 60 0.46651329801849117
		 61 0.45161401140131396 62 0.43712636569329766 63 0.42274523194460223 64 0.4084116735550305
		 65 0.39525506887470163 66 0.38118175680833899 67 0.3669666098295925 68 0.35265210426523286
		 69 0.33879223706193584 70 0.32352243915116985 71 0.30806656445743363 72 0.29490682374471577
		 73 0.28091519154662736 74 0.26621836766430551 75 0.25063725152241312 76 0.2363626646179009
		 77 0.22040346982753312 78 0.20516123305452127 79 0.19026080612445639 80 0.17569070396184738
		 81 0.1621988474849303 82 0.14826967885636 83 0.13340458277298406 84 0.11894461980489957
		 85 0.10533657003398245 86 0.089675734530583417 87 0.074728846289866202 88 0.060019299082145205
		 89 0.044931179158120838 90 0.029685785811779275 91 0.014929386335214567 92 -0.00098438403728995372
		 93 -0.017134506680624495 94 -0.032719829485320873;
createNode animCurveTL -n "marker_14_MKR_translateY";
	rename -uid "B6A634AA-46B1-54D1-974A-5FBAA58D5A9B";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 36 ".ktv[0:35]"  59 0.46267734398397753 60 0.45866574757857548
		 61 0.45242144714422794 62 0.44798017993237527 63 0.44232996700545479 64 0.43864617138556861
		 65 0.43627051373035819 66 0.43543613711487261 67 0.4326828952249212 68 0.42900076722605296
		 69 0.42678390624734985 70 0.42492645589620626 71 0.42247484903362331 72 0.41988818244793846
		 73 0.41864828205334714 74 0.41792257874976557 75 0.41697124860904233 76 0.41443324216956934
		 77 0.41204221244273576 78 0.41035451769326781 79 0.40810530948571178 80 0.40444400903873845
		 81 0.40220143709058065 82 0.39957807844351956 83 0.39832839212135673 84 0.39817014429537201
		 85 0.39846058682834062 86 0.39868712278373453 87 0.39666909419768537 88 0.39461868278584444
		 89 0.39340599366442708 90 0.39369491498294806 91 0.39517359345317893 92 0.39487552401904991
		 93 0.39268170015955395 94 0.38987332208411296;
createNode animCurveTU -n "marker_14_MKR_enable";
	rename -uid "2386A56F-4E73-6CBC-EDF4-8F9C8874769A";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 37 ".ktv[0:36]"  58 0 59 1 60 1 61 1 62 1 63 1 64 1 65 1
		 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1 79 1 80 1 81 1 82 1
		 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1;
createNode animCurveTU -n "marker_14_MKR_weight";
	rename -uid "EE83EA20-49CC-880F-7809-83A55B21BD25";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 36 ".ktv[0:35]"  59 1 60 1 61 1 62 1 63 1 64 1 65 1 66 1
		 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1 79 1 80 1 81 1 82 1 83 1
		 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1;
createNode script -n "uiConfigurationScriptNode";
	rename -uid "1992F1FE-4CB1-3F55-50E7-209C75A19C9D";
	setAttr ".b" -type "string" (
		"// Maya Mel UI Configuration File.\n//\n//  This script is machine generated.  Edit at your own risk.\n//\n//\n\nglobal string $gMainPane;\nif (`paneLayout -exists $gMainPane`) {\n\n\tglobal int $gUseScenePanelConfig;\n\tint    $useSceneConfig = $gUseScenePanelConfig;\n\tint    $nodeEditorPanelVisible = stringArrayContains(\"nodeEditorPanel1\", `getPanel -vis`);\n\tint    $nodeEditorWorkspaceControlOpen = (`workspaceControl -exists nodeEditorPanel1Window` && `workspaceControl -q -visible nodeEditorPanel1Window`);\n\tint    $menusOkayInPanels = `optionVar -q allowMenusInPanels`;\n\tint    $nVisPanes = `paneLayout -q -nvp $gMainPane`;\n\tint    $nPanes = 0;\n\tstring $editorName;\n\tstring $panelName;\n\tstring $itemFilterName;\n\tstring $panelConfig;\n\n\t//\n\t//  get current state of the UI\n\t//\n\tsceneUIReplacement -update $gMainPane;\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Top View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Top View\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"top\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n"
		+ "            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n"
		+ "            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 786\n            -height 711\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n"
		+ "\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Side View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Side View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"side\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n"
		+ "            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n"
		+ "            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 0\n            -height 711\n"
		+ "            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Front View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Front View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"front\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n"
		+ "            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n"
		+ "            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n"
		+ "            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 789\n            -height 711\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Persp View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"stA_1_1Shape1\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n"
		+ "            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n"
		+ "            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 0\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n"
		+ "            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1277\n            -height 711\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"ToggledOutliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"ToggledOutliner\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 1\n            -showReferenceMembers 1\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n"
		+ "            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -isSet 0\n            -isSetMember 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            -renderFilterIndex 0\n            -selectionOrder \"chronological\" \n            -expandAttribute 0\n            $editorName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"Outliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 0\n            -showReferenceMembers 0\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n"
		+ "            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -isSet 0\n            -isSetMember 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n"
		+ "            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            -renderFilterIndex 0\n            -selectionOrder \"chronological\" \n            -expandAttribute 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"graphEditor\" (localizedPanelLabel(\"Graph Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n"
		+ "                -showMuteInfo 0\n                -organizeByLayer 1\n                -organizeByClip 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showParentContainers 1\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 1\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 1\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n"
		+ "                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 1\n                -displayInfinities 0\n"
		+ "                -displayValues 0\n                -autoFit 1\n                -autoFitTime 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -showResults \"off\" \n                -showBufferCurves \"off\" \n                -smoothness \"fine\" \n                -resultSamples 1\n                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -showCurveNames 0\n                -showActiveCurveNames 0\n                -stackedCurves 0\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -displayNormalized 0\n                -preSelectionHighlight 0\n                -constrainDrag 0\n                -classicMode 1\n                -valueLinesToggle 1\n                -outliner \"graphEditor1OutlineEd\" \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dopeSheetPanel\" (localizedPanelLabel(\"Dope Sheet\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dope Sheet\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -organizeByClip 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 0\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showParentContainers 1\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n"
		+ "                -showUpstreamCurves 1\n                -showUnitlessCurves 0\n                -showCompounds 1\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 0\n                -doNotSelectNewObjects 1\n                -dropIsParent 1\n                -transmitFilters 0\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n"
		+ "                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"DopeSheetEd\");\n            dopeSheetEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -autoFitTime 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -outliner \"dopeSheetPanel1OutlineEd\" \n                -showSummary 1\n                -showScene 0\n                -hierarchyBelow 0\n                -showTicks 1\n                -selectionWindow 0 0 0 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"timeEditorPanel\" (localizedPanelLabel(\"Time Editor\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Time Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"clipEditorPanel\" (localizedPanelLabel(\"Trax Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Trax Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = clipEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -autoFitTime 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 0 \n                $editorName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"sequenceEditorPanel\" (localizedPanelLabel(\"Camera Sequencer\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Camera Sequencer\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = sequenceEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -autoFitTime 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 1 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperGraphPanel\" (localizedPanelLabel(\"Hypergraph Hierarchy\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypergraph Hierarchy\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"HyperGraphEd\");\n            hyperGraph -e \n                -graphLayoutStyle \"hierarchicalLayout\" \n                -orientation \"horiz\" \n                -mergeConnections 1\n                -zoom 1\n                -animateTransition 0\n                -showRelationships 1\n                -showShapes 0\n                -showDeformers 0\n                -showExpressions 0\n                -showConstraints 0\n                -showConnectionFromSelected 0\n                -showConnectionToSelected 0\n                -showConstraintLabels 0\n                -showUnderworld 0\n                -showInvisible 0\n                -transitionFrames 1\n                -opaqueContainers 0\n                -freeform 0\n                -imagePosition 0 0 \n                -imageScale 1\n                -imageEnabled 0\n                -graphType \"DAG\" \n"
		+ "                -heatMapDisplay 0\n                -updateSelection 1\n                -updateNodeAdded 1\n                -useDrawOverrideColor 0\n                -limitGraphTraversal -1\n                -range 0 0 \n                -iconSize \"smallIcons\" \n                -showCachedConnections 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperShadePanel\" (localizedPanelLabel(\"Hypershade\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypershade\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"visorPanel\" (localizedPanelLabel(\"Visor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Visor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n"
		+ "\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"nodeEditorPanel\" (localizedPanelLabel(\"Node Editor\")) `;\n\tif ($nodeEditorPanelVisible || $nodeEditorWorkspaceControlOpen) {\n\t\tif (\"\" == $panelName) {\n\t\t\tif ($useSceneConfig) {\n\t\t\t\t$panelName = `scriptedPanel -unParent  -type \"nodeEditorPanel\" -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -connectNodeOnCreation 0\n                -connectOnDrop 0\n                -copyConnectionsOnPaste 0\n                -connectionStyle \"bezier\" \n                -defaultPinnedState 0\n                -additiveGraphingMode 0\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n"
		+ "                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -crosshairOnEdgeDragging 0\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                -editorMode \"default\" \n                $editorName;\n\t\t\t}\n\t\t} else {\n\t\t\t$label = `panel -q -label $panelName`;\n\t\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -connectNodeOnCreation 0\n                -connectOnDrop 0\n                -copyConnectionsOnPaste 0\n"
		+ "                -connectionStyle \"bezier\" \n                -defaultPinnedState 0\n                -additiveGraphingMode 0\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -crosshairOnEdgeDragging 0\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                -editorMode \"default\" \n                $editorName;\n\t\t\tif (!$useSceneConfig) {\n\t\t\t\tpanel -e -l $label $panelName;\n\t\t\t}\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"createNodePanel\" (localizedPanelLabel(\"Create Node\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n"
		+ "\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Create Node\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"polyTexturePlacementPanel\" (localizedPanelLabel(\"UV Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"UV Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"renderWindowPanel\" (localizedPanelLabel(\"Render View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Render View\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"shapePanel\" (localizedPanelLabel(\"Shape Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n"
		+ "\t\tshapePanel -edit -l (localizedPanelLabel(\"Shape Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"posePanel\" (localizedPanelLabel(\"Pose Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tposePanel -edit -l (localizedPanelLabel(\"Pose Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynRelEdPanel\" (localizedPanelLabel(\"Dynamic Relationships\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dynamic Relationships\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"relationshipPanel\" (localizedPanelLabel(\"Relationship Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n"
		+ "\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Relationship Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"referenceEditorPanel\" (localizedPanelLabel(\"Reference Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Reference Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"componentEditorPanel\" (localizedPanelLabel(\"Component Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Component Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynPaintScriptedPanelType\" (localizedPanelLabel(\"Paint Effects\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Paint Effects\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"scriptEditorPanel\" (localizedPanelLabel(\"Script Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Script Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"profilerPanel\" (localizedPanelLabel(\"Profiler Tool\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Profiler Tool\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"contentBrowserPanel\" (localizedPanelLabel(\"Content Browser\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Content Browser\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperGraphPanel\" (localizedPanelLabel(\"Hypergraph InputOutput2\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypergraph InputOutput2\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"HyperGraphEd\");\n            hyperGraph -e \n                -graphLayoutStyle \"hierarchicalLayout\" \n                -orientation \"horiz\" \n                -mergeConnections 1\n                -zoom 1\n                -animateTransition 0\n                -showRelationships 1\n                -showShapes 0\n                -showDeformers 0\n                -showExpressions 0\n                -showConstraints 0\n                -showConnectionFromSelected 0\n                -showConnectionToSelected 0\n"
		+ "                -showConstraintLabels 0\n                -showUnderworld 0\n                -showInvisible 0\n                -transitionFrames 1\n                -opaqueContainers 0\n                -freeform 0\n                -imagePosition 0 0 \n                -imageScale 1\n                -imageEnabled 0\n                -graphType \"DAG\" \n                -heatMapDisplay 0\n                -updateSelection 1\n                -updateNodeAdded 1\n                -useDrawOverrideColor 0\n                -limitGraphTraversal -1\n                -range 0 0 \n                -iconSize \"smallIcons\" \n                -showCachedConnections 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\tif ($useSceneConfig) {\n        string $configName = `getPanel -cwl (localizedPanelLabel(\"Current Layout\"))`;\n        if (\"\" != $configName) {\n\t\t\tpanelConfiguration -edit -label (localizedPanelLabel(\"Current Layout\")) \n\t\t\t\t-userCreated false\n\t\t\t\t-defaultImage \"\"\n\t\t\t\t-image \"\"\n\t\t\t\t-sc false\n\t\t\t\t-configString \"global string $gMainPane; paneLayout -e -cn \\\"vertical2\\\" -ps 1 20 100 -ps 2 80 100 $gMainPane;\"\n"
		+ "\t\t\t\t-removeAllPanels\n\t\t\t\t-ap false\n\t\t\t\t\t(localizedPanelLabel(\"Outliner\")) \n\t\t\t\t\t\"outlinerPanel\"\n\t\t\t\t\t\"$panelName = `outlinerPanel -unParent -l (localizedPanelLabel(\\\"Outliner\\\")) -mbv $menusOkayInPanels `;\\n$editorName = $panelName;\\noutlinerEditor -e \\n    -showShapes 0\\n    -showAssignedMaterials 0\\n    -showTimeEditor 1\\n    -showReferenceNodes 0\\n    -showReferenceMembers 0\\n    -showAttributes 0\\n    -showConnected 0\\n    -showAnimCurvesOnly 0\\n    -showMuteInfo 0\\n    -organizeByLayer 1\\n    -organizeByClip 1\\n    -showAnimLayerWeight 1\\n    -autoExpandLayers 1\\n    -autoExpand 0\\n    -showDagOnly 1\\n    -showAssets 1\\n    -showContainedOnly 1\\n    -showPublishedAsConnected 0\\n    -showParentContainers 0\\n    -showContainerContents 1\\n    -ignoreDagHierarchy 0\\n    -expandConnections 0\\n    -showUpstreamCurves 1\\n    -showUnitlessCurves 1\\n    -showCompounds 1\\n    -showLeafs 1\\n    -showNumericAttrsOnly 0\\n    -highlightActive 1\\n    -autoSelectNewObjects 0\\n    -doNotSelectNewObjects 0\\n    -dropIsParent 1\\n    -transmitFilters 0\\n    -setFilter \\\"defaultSetFilter\\\" \\n    -showSetMembers 1\\n    -allowMultiSelection 1\\n    -alwaysToggleSelect 0\\n    -directSelect 0\\n    -isSet 0\\n    -isSetMember 0\\n    -displayMode \\\"DAG\\\" \\n    -expandObjects 0\\n    -setsIgnoreFilters 1\\n    -containersIgnoreFilters 0\\n    -editAttrName 0\\n    -showAttrValues 0\\n    -highlightSecondary 0\\n    -showUVAttrsOnly 0\\n    -showTextureNodesOnly 0\\n    -attrAlphaOrder \\\"default\\\" \\n    -animLayerFilterOptions \\\"allAffecting\\\" \\n    -sortOrder \\\"none\\\" \\n    -longNames 0\\n    -niceNames 1\\n    -showNamespace 1\\n    -showPinIcons 0\\n    -mapMotionTrails 0\\n    -ignoreHiddenAttribute 0\\n    -ignoreOutlinerColor 0\\n    -renderFilterVisible 0\\n    -renderFilterIndex 0\\n    -selectionOrder \\\"chronological\\\" \\n    -expandAttribute 0\\n    $editorName\"\n"
		+ "\t\t\t\t\t\"outlinerPanel -edit -l (localizedPanelLabel(\\\"Outliner\\\")) -mbv $menusOkayInPanels  $panelName;\\n$editorName = $panelName;\\noutlinerEditor -e \\n    -showShapes 0\\n    -showAssignedMaterials 0\\n    -showTimeEditor 1\\n    -showReferenceNodes 0\\n    -showReferenceMembers 0\\n    -showAttributes 0\\n    -showConnected 0\\n    -showAnimCurvesOnly 0\\n    -showMuteInfo 0\\n    -organizeByLayer 1\\n    -organizeByClip 1\\n    -showAnimLayerWeight 1\\n    -autoExpandLayers 1\\n    -autoExpand 0\\n    -showDagOnly 1\\n    -showAssets 1\\n    -showContainedOnly 1\\n    -showPublishedAsConnected 0\\n    -showParentContainers 0\\n    -showContainerContents 1\\n    -ignoreDagHierarchy 0\\n    -expandConnections 0\\n    -showUpstreamCurves 1\\n    -showUnitlessCurves 1\\n    -showCompounds 1\\n    -showLeafs 1\\n    -showNumericAttrsOnly 0\\n    -highlightActive 1\\n    -autoSelectNewObjects 0\\n    -doNotSelectNewObjects 0\\n    -dropIsParent 1\\n    -transmitFilters 0\\n    -setFilter \\\"defaultSetFilter\\\" \\n    -showSetMembers 1\\n    -allowMultiSelection 1\\n    -alwaysToggleSelect 0\\n    -directSelect 0\\n    -isSet 0\\n    -isSetMember 0\\n    -displayMode \\\"DAG\\\" \\n    -expandObjects 0\\n    -setsIgnoreFilters 1\\n    -containersIgnoreFilters 0\\n    -editAttrName 0\\n    -showAttrValues 0\\n    -highlightSecondary 0\\n    -showUVAttrsOnly 0\\n    -showTextureNodesOnly 0\\n    -attrAlphaOrder \\\"default\\\" \\n    -animLayerFilterOptions \\\"allAffecting\\\" \\n    -sortOrder \\\"none\\\" \\n    -longNames 0\\n    -niceNames 1\\n    -showNamespace 1\\n    -showPinIcons 0\\n    -mapMotionTrails 0\\n    -ignoreHiddenAttribute 0\\n    -ignoreOutlinerColor 0\\n    -renderFilterVisible 0\\n    -renderFilterIndex 0\\n    -selectionOrder \\\"chronological\\\" \\n    -expandAttribute 0\\n    $editorName\"\n"
		+ "\t\t\t\t-ap false\n\t\t\t\t\t(localizedPanelLabel(\"Persp View\")) \n\t\t\t\t\t\"modelPanel\"\n"
		+ "\t\t\t\t\t\"$panelName = `modelPanel -unParent -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels `;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -camera \\\"stA_1_1Shape1\\\" \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 16384\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 0\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1277\\n    -height 711\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t\t\"modelPanel -edit -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels  $panelName;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -camera \\\"stA_1_1Shape1\\\" \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 16384\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 0\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1277\\n    -height 711\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t$configName;\n\n            setNamedPanelLayout (localizedPanelLabel(\"Current Layout\"));\n        }\n\n        panelHistory -e -clear mainPanelHistory;\n        sceneUIReplacement -clear;\n\t}\n\n\ngrid -spacing 5 -size 12 -divisions 5 -displayAxes yes -displayGridLines yes -displayDivisionLines yes -displayPerspectiveLabels no -displayOrthographicLabels no -displayAxesBold yes -perspectiveLabelPosition axis -orthographicLabelPosition edge;\nviewManip -drawCompass 0 -compassAngle 0 -frontParameters \"\" -homeParameters \"\" -selectionLockParameters \"\";\n}\n");
	setAttr ".st" 3;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "83BF5419-4227-686F-CA61-ACAE97021268";
	setAttr ".b" -type "string" "playbackOptions -min 0 -max 94 -ast 0 -aet 94 ";
	setAttr ".st" 6;
select -ne :time1;
	setAttr ".o" 30;
	setAttr ".unw" 30;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 4 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultResolution;
	setAttr ".w" 1936;
	setAttr ".h" 1288;
	setAttr ".pa" 1;
	setAttr ".dar" 1.503105640411377;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
connectAttr "stA_1_1_translateX.o" "stA_1_1.tx";
connectAttr "stA_1_1_translateY.o" "stA_1_1.ty";
connectAttr "stA_1_1_translateZ.o" "stA_1_1.tz";
connectAttr "stA_1_1_rotateX.o" "stA_1_1.rx";
connectAttr "stA_1_1_rotateY.o" "stA_1_1.ry";
connectAttr "stA_1_1_rotateZ.o" "stA_1_1.rz";
connectAttr "imagePlaneShape1.msg" "stA_1_1Shape1.ip" -na;
connectAttr "stA_1_1Shape1_focalLength.o" "stA_1_1Shape1.fl";
connectAttr ":defaultColorMgtGlobals.cme" "imagePlaneShape1.cme";
connectAttr ":defaultColorMgtGlobals.cfe" "imagePlaneShape1.cmcf";
connectAttr ":defaultColorMgtGlobals.cfp" "imagePlaneShape1.cmcp";
connectAttr ":defaultColorMgtGlobals.wsn" "imagePlaneShape1.ws";
connectAttr "frame_ext_expression.out[0]" "imagePlaneShape1.fe";
connectAttr "mmMarkerScale1.ot" "markerGroup1.t";
connectAttr "mmMarkerScale1.os" "markerGroup1.s";
connectAttr "marker_01_MKR_translateX.o" "marker_01_MKR.tx" -l on;
connectAttr "marker_01_MKR_translateY.o" "marker_01_MKR.ty" -l on;
connectAttr "marker_01_MKR_enable.o" "marker_01_MKR.enable";
connectAttr "marker_01_MKR_weight.o" "marker_01_MKR.weight";
connectAttr "marker_01_MKR.enable" "marker_01_MKR.lodv";
connectAttr "bundle_01_BND.msg" "marker_01_MKR.bundle";
connectAttr "marker_02_MKR_translateX.o" "marker_02_MKR.tx" -l on;
connectAttr "marker_02_MKR_translateY.o" "marker_02_MKR.ty" -l on;
connectAttr "marker_02_MKR_enable.o" "marker_02_MKR.enable";
connectAttr "marker_02_MKR_weight.o" "marker_02_MKR.weight";
connectAttr "marker_02_MKR.enable" "marker_02_MKR.lodv";
connectAttr "bundle_02_BND.msg" "marker_02_MKR.bundle";
connectAttr "marker_03_MKR_translateX.o" "marker_03_MKR.tx" -l on;
connectAttr "marker_03_MKR_translateY.o" "marker_03_MKR.ty" -l on;
connectAttr "marker_03_MKR_enable.o" "marker_03_MKR.enable";
connectAttr "marker_03_MKR_weight.o" "marker_03_MKR.weight";
connectAttr "marker_03_MKR.enable" "marker_03_MKR.lodv";
connectAttr "bundle_03_BND.msg" "marker_03_MKR.bundle";
connectAttr "marker_04_MKR_translateX.o" "marker_04_MKR.tx" -l on;
connectAttr "marker_04_MKR_translateY.o" "marker_04_MKR.ty" -l on;
connectAttr "marker_04_MKR_enable.o" "marker_04_MKR.enable";
connectAttr "marker_04_MKR_weight.o" "marker_04_MKR.weight";
connectAttr "marker_04_MKR.enable" "marker_04_MKR.lodv";
connectAttr "bundle_04_BND.msg" "marker_04_MKR.bundle";
connectAttr "marker_05_MKR_translateX.o" "marker_05_MKR.tx" -l on;
connectAttr "marker_05_MKR_translateY.o" "marker_05_MKR.ty" -l on;
connectAttr "marker_05_MKR_enable.o" "marker_05_MKR.enable";
connectAttr "marker_05_MKR_weight.o" "marker_05_MKR.weight";
connectAttr "marker_05_MKR.enable" "marker_05_MKR.lodv";
connectAttr "bundle_05_BND.msg" "marker_05_MKR.bundle";
connectAttr "marker_06_MKR_translateX.o" "marker_06_MKR.tx" -l on;
connectAttr "marker_06_MKR_translateY.o" "marker_06_MKR.ty" -l on;
connectAttr "marker_06_MKR_enable.o" "marker_06_MKR.enable";
connectAttr "marker_06_MKR_weight.o" "marker_06_MKR.weight";
connectAttr "marker_06_MKR.enable" "marker_06_MKR.lodv";
connectAttr "bundle_06_BND.msg" "marker_06_MKR.bundle";
connectAttr "marker_07_MKR_translateX.o" "marker_07_MKR.tx" -l on;
connectAttr "marker_07_MKR_translateY.o" "marker_07_MKR.ty" -l on;
connectAttr "marker_07_MKR_enable.o" "marker_07_MKR.enable";
connectAttr "marker_07_MKR_weight.o" "marker_07_MKR.weight";
connectAttr "marker_07_MKR.enable" "marker_07_MKR.lodv";
connectAttr "bundle_07_BND.msg" "marker_07_MKR.bundle";
connectAttr "marker_08_MKR_translateX.o" "marker_08_MKR.tx" -l on;
connectAttr "marker_08_MKR_translateY.o" "marker_08_MKR.ty" -l on;
connectAttr "marker_08_MKR_enable.o" "marker_08_MKR.enable";
connectAttr "marker_08_MKR_weight.o" "marker_08_MKR.weight";
connectAttr "marker_08_MKR.enable" "marker_08_MKR.lodv";
connectAttr "bundle_08_BND.msg" "marker_08_MKR.bundle";
connectAttr "marker_09_MKR_translateX.o" "marker_09_MKR.tx" -l on;
connectAttr "marker_09_MKR_translateY.o" "marker_09_MKR.ty" -l on;
connectAttr "marker_09_MKR_enable.o" "marker_09_MKR.enable";
connectAttr "marker_09_MKR_weight.o" "marker_09_MKR.weight";
connectAttr "marker_09_MKR.enable" "marker_09_MKR.lodv";
connectAttr "bundle_09_BND.msg" "marker_09_MKR.bundle";
connectAttr "marker_10_MKR_translateX.o" "marker_10_MKR.tx" -l on;
connectAttr "marker_10_MKR_translateY.o" "marker_10_MKR.ty" -l on;
connectAttr "marker_10_MKR_enable.o" "marker_10_MKR.enable";
connectAttr "marker_10_MKR_weight.o" "marker_10_MKR.weight";
connectAttr "marker_10_MKR.enable" "marker_10_MKR.lodv";
connectAttr "bundle_10_BND.msg" "marker_10_MKR.bundle";
connectAttr "marker_11_MKR_translateX.o" "marker_11_MKR.tx" -l on;
connectAttr "marker_11_MKR_translateY.o" "marker_11_MKR.ty" -l on;
connectAttr "marker_11_MKR_enable.o" "marker_11_MKR.enable";
connectAttr "marker_11_MKR_weight.o" "marker_11_MKR.weight";
connectAttr "marker_11_MKR.enable" "marker_11_MKR.lodv";
connectAttr "bundle_11_BND.msg" "marker_11_MKR.bundle";
connectAttr "marker_12_MKR_translateX.o" "marker_12_MKR.tx" -l on;
connectAttr "marker_12_MKR_translateY.o" "marker_12_MKR.ty" -l on;
connectAttr "marker_12_MKR_enable.o" "marker_12_MKR.enable";
connectAttr "marker_12_MKR_weight.o" "marker_12_MKR.weight";
connectAttr "marker_12_MKR.enable" "marker_12_MKR.lodv";
connectAttr "bundle_12_BND.msg" "marker_12_MKR.bundle";
connectAttr "marker_13_MKR_translateX.o" "marker_13_MKR.tx" -l on;
connectAttr "marker_13_MKR_translateY.o" "marker_13_MKR.ty" -l on;
connectAttr "marker_13_MKR_enable.o" "marker_13_MKR.enable";
connectAttr "marker_13_MKR_weight.o" "marker_13_MKR.weight";
connectAttr "marker_13_MKR.enable" "marker_13_MKR.lodv";
connectAttr "bundle_13_BND.msg" "marker_13_MKR.bundle";
connectAttr "marker_14_MKR_translateX.o" "marker_14_MKR.tx" -l on;
connectAttr "marker_14_MKR_translateY.o" "marker_14_MKR.ty" -l on;
connectAttr "marker_14_MKR_enable.o" "marker_14_MKR.enable";
connectAttr "marker_14_MKR_weight.o" "marker_14_MKR.weight";
connectAttr "marker_14_MKR.enable" "marker_14_MKR.lodv";
connectAttr "bundle_14_BND.msg" "marker_14_MKR.bundle";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr ":time1.o" "frame_ext_expression.tim";
connectAttr "markerGroup1.depth" "mmMarkerScale1.dpt";
connectAttr "markerGroup1.overscan" "mmMarkerScale1.ovrscn";
connectAttr "stA_1_1Shape1.fl" "mmMarkerScale1.fl";
connectAttr "stA_1_1Shape1.cap" "mmMarkerScale1.cap";
connectAttr "stA_1_1Shape1.fio" "mmMarkerScale1.fio";
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
// End of stA.ma
