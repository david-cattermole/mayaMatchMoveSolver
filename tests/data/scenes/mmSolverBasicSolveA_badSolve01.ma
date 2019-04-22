//Maya ASCII 2017 scene
//Name: mmSolverBasicSolveA_badSolve01.ma
//Last modified: Sun, Mar 24, 2019 05:12:28 PM
//Codeset: 1252
requires maya "2017";
requires -nodeType "mmMarkerScale" -nodeType "mmMarkerGroupTransform" "mmSolver" "0.2.0";
requires "stereoCamera" "10.0";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2017";
fileInfo "version" "2017";
fileInfo "cutIdentifier" "201606150345-997974";
fileInfo "osv" "Microsoft Windows 8 Business Edition, 64-bit  (Build 9200)\n";
createNode transform -s -n "persp";
	rename -uid "C3CAF448-4692-10EA-0322-42B622393CAE";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -7.0527749834641504 42.491360844753387 4.0806506635042998 ;
	setAttr ".r" -type "double3" -76.538352729602011 32.600000000000023 3.7753524030112443e-015 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "EE023BE9-4BD1-BFF5-5E82-2286EF22E19B";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 35.196477096167591;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".tp" -type "double3" -11.467216931364476 8.261872938460721 -2.8220198300529846 ;
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "BFB95C81-4F43-36CE-09E5-E8BF3D674E45";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -90 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "A9C26E5E-4F19-9F5C-0ECB-B697E4BE326B";
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
	rename -uid "CA20F756-4259-7ABD-7701-508DC4DC5F4B";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "792BF698-4C23-84AF-31A4-31874634FDDC";
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
	rename -uid "300D2599-4932-9631-E42B-87BC7D682E29";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 90 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "5D9D897E-4476-BBCD-BE2D-A387B9622980";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "camera1";
	rename -uid "0CCA5AC0-4C27-4548-92DF-D3BF31017BBF";
	setAttr ".rp" -type "double3" 1.2212453270876722e-015 1.1102230246251565e-016 0 ;
	setAttr ".rpt" -type "double3" -3.1974821183355083e-015 -1.6966114055053635e-015 
		-2.639883759912914e-015 ;
createNode camera -n "cameraShape1" -p "camera1";
	rename -uid "EB805B09-4A6A-658E-0887-A0A28FDACCE6";
	setAttr -k off ".v";
	setAttr ".rnd" no;
	setAttr ".cap" -type "double2" 1.98 1.08 ;
	setAttr ".ff" 0;
	setAttr ".ovr" 1.3;
	setAttr ".pn" -type "double2" 0.21218189375621024 0.13500780574553672 ;
	setAttr ".zom" 0.14201667044562652;
	setAttr ".coi" 31.041190787483536;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "camera1";
	setAttr ".den" -type "string" "camera1_depth";
	setAttr ".man" -type "string" "camera1_mask";
	setAttr ".dfg" yes;
createNode transform -n "imagePlane1" -p "cameraShape1";
	rename -uid "73301B90-42D5-9531-4A21-BD896F97F962";
createNode imagePlane -n "imagePlaneShape1" -p "imagePlane1";
	rename -uid "EA33BBA1-4672-83D4-5505-37B9FC40FAE1";
	setAttr -k off ".v";
	setAttr ".fc" 204;
	setAttr ".imn" -type "string" "C:/Users/Anil Reddy/Documents/maya/projects/mmSolver//images/backPlate/mayaprimetives.0001.tga";
	setAttr ".ufe" yes;
	setAttr ".cov" -type "short2" 1980 1080 ;
	setAttr ".s" -type "double2" 1.98 1.08 ;
	setAttr ".w" 19.8;
	setAttr ".h" 10.799999999999999;
	setAttr ".cs" -type "string" "Raw";
createNode mmMarkerGroupTransform -n "markerGroup1" -p "camera1";
	rename -uid "3C3E3A48-46E9-ED62-8AE2-E880F5DA4EF6";
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
createNode transform -n "pCube1_locator9_MKR" -p "markerGroup1";
	rename -uid "B95F4915-4441-03B3-1750-F197C1D839D4";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" -0.2350533236411263 0.32344938891728636 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "|pCube1|locator9";
createNode locator -n "pCube1_locator9_MKRShape" -p "pCube1_locator9_MKR";
	rename -uid "79F10218-4479-4144-81A0-87924D0B58FB";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "pCube1_locator10_MKR" -p "markerGroup1";
	rename -uid "E445DC05-48D0-FA7B-38F6-B4B7CC257BA3";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" -0.1610888478373646 0.39102797588829374 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "|pCube1|locator10";
createNode locator -n "pCube1_locator10_MKRShape" -p "pCube1_locator10_MKR";
	rename -uid "596BA1C2-47FE-9595-797F-7F8339F66771";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "pCube1_locator11_MKR" -p "markerGroup1";
	rename -uid "C5E9111C-4A4B-B54C-55AE-03BF8E8CF807";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" -0.21257663668063131 0.27591592386940278 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "|pCube1|locator11";
createNode locator -n "pCube1_locator11_MKRShape" -p "pCube1_locator11_MKR";
	rename -uid "A3E0F305-4AEC-2FA2-68C8-3DA55BEA6B8E";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "pCube1_locator12_MKR" -p "markerGroup1";
	rename -uid "22D2F000-4316-86FE-A7D7-6DAA2C2F87B1";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" -0.15392195093387917 0.35898686928700696 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "|pCube1|locator12";
createNode locator -n "pCube1_locator12_MKRShape" -p "pCube1_locator12_MKR";
	rename -uid "0F095D3B-466E-6A86-A879-2F9AA2625D2C";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "locator1_MKR" -p "markerGroup1";
	rename -uid "E7A274D1-4ED2-CABB-F8FB-B48052A76FC5";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" -0.048036164481001231 0.15045022680067976 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "|locator1";
createNode locator -n "locator1_MKRShape" -p "locator1_MKR";
	rename -uid "CDC1116C-4EC5-BD6F-584F-6B8673A439F3";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "locator2_MKR" -p "markerGroup1";
	rename -uid "1AECA758-4EE5-A7EE-2A58-8C986164F603";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" -0.1797218475501316 0.027284137036894807 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "|locator2";
createNode locator -n "locator2_MKRShape" -p "locator2_MKR";
	rename -uid "B638AB5F-4B13-F0FA-2A52-59A2A505962A";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "locator3_MKR" -p "markerGroup1";
	rename -uid "066F00A2-413B-2E7A-EABB-E8827DB8223E";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" 0.0078009326924349809 -0.11996857180285653 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "|locator3";
createNode locator -n "locator3_MKRShape" -p "locator3_MKR";
	rename -uid "DAF2DCA3-4996-0B12-776B-2EAA473AAB46";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "locator4_MKR" -p "markerGroup1";
	rename -uid "CBCCB22C-4875-B8B0-917A-4C9554F7FAE5";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" 0.036598963896994463 -0.04542887310005761 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "|locator4";
createNode locator -n "locator4_MKRShape" -p "locator4_MKR";
	rename -uid "D33C24F3-4DCA-479D-C9DE-6BA6C4DC4243";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "locator5_MKR" -p "markerGroup1";
	rename -uid "7C76417E-45DB-E907-CCA6-5789DAE7202D";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" 0.097626102757820465 0.065300604598534151 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "|locator5";
createNode locator -n "locator5_MKRShape" -p "locator5_MKR";
	rename -uid "3D81E8ED-44FA-F503-6796-5FADBABE924E";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "locator6_MKR" -p "markerGroup1";
	rename -uid "8B9F42DC-424A-4A6F-0BFF-9784F21198E9";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" 0.12019222232328097 0.17699277427246907 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "|locator6";
createNode locator -n "locator6_MKRShape" -p "locator6_MKR";
	rename -uid "5E11DE99-46AF-95DE-5CC4-BEB4E3B240FF";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "locator7_MKR" -p "markerGroup1";
	rename -uid "47DEC7EE-48B4-4F21-6C8E-3D837F247A79";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" -0.082701979284366678 -0.076759125856007249 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "|locator7";
createNode locator -n "locator7_MKRShape" -p "locator7_MKR";
	rename -uid "ADE33001-495B-C341-4DEC-60A7675C72CB";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "locator8_MKR" -p "markerGroup1";
	rename -uid "A9A5BA38-4676-CDC8-88E6-818955089A6D";
	addAttr -ci true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" 0.17733850258798134 -0.050010338697136669 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -cb on ".enable";
	setAttr -cb on ".weight";
	setAttr -l on ".markerName" -type "string" "|locator8";
createNode locator -n "locator8_MKRShape" -p "locator8_MKR";
	rename -uid "0CDC5BD9-4D2D-9459-8448-6DA0EC301F18";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "group1";
	rename -uid "8E56F99C-4315-2242-2863-F6AB3149259D";
createNode transform -n "geom:pPlane1" -p "group1";
	rename -uid "3ADB4C59-47D0-1EEE-32DB-9597D029134E";
createNode mesh -n "geom:pPlane1Shape" -p "geom:pPlane1";
	rename -uid "58AFA9E2-4EDA-948D-EA6B-38804880BBD3";
	setAttr -k off ".v";
	setAttr ".iog[0].og[0].gcl" -type "componentList" 1 "f[0:99]";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 121 ".uvst[0].uvsp[0:120]" -type "float2" 0 0 0.1 0 0.1 0.1
		 0 0.1 0.2 0 0.2 0.1 0.30000001 0 0.30000001 0.1 0.40000001 0 0.40000001 0.1 0.5 0
		 0.5 0.1 0.60000002 0 0.60000002 0.1 0.69999999 0 0.69999999 0.1 0.80000001 0 0.80000001
		 0.1 0.89999998 0 0.89999998 0.1 1 0 1 0.1 0.1 0.2 0 0.2 0.2 0.2 0.30000001 0.2 0.40000001
		 0.2 0.5 0.2 0.60000002 0.2 0.69999999 0.2 0.80000001 0.2 0.89999998 0.2 1 0.2 0.1
		 0.30000001 0 0.30000001 0.2 0.30000001 0.30000001 0.30000001 0.40000001 0.30000001
		 0.5 0.30000001 0.60000002 0.30000001 0.69999999 0.30000001 0.80000001 0.30000001
		 0.89999998 0.30000001 1 0.30000001 0.1 0.40000001 0 0.40000001 0.2 0.40000001 0.30000001
		 0.40000001 0.40000001 0.40000001 0.5 0.40000001 0.60000002 0.40000001 0.69999999
		 0.40000001 0.80000001 0.40000001 0.89999998 0.40000001 1 0.40000001 0.1 0.5 0 0.5
		 0.2 0.5 0.30000001 0.5 0.40000001 0.5 0.5 0.5 0.60000002 0.5 0.69999999 0.5 0.80000001
		 0.5 0.89999998 0.5 1 0.5 0.1 0.60000002 0 0.60000002 0.2 0.60000002 0.30000001 0.60000002
		 0.40000001 0.60000002 0.5 0.60000002 0.60000002 0.60000002 0.69999999 0.60000002
		 0.80000001 0.60000002 0.89999998 0.60000002 1 0.60000002 0.1 0.69999999 0 0.69999999
		 0.2 0.69999999 0.30000001 0.69999999 0.40000001 0.69999999 0.5 0.69999999 0.60000002
		 0.69999999 0.69999999 0.69999999 0.80000001 0.69999999 0.89999998 0.69999999 1 0.69999999
		 0.1 0.80000001 0 0.80000001 0.2 0.80000001 0.30000001 0.80000001 0.40000001 0.80000001
		 0.5 0.80000001 0.60000002 0.80000001 0.69999999 0.80000001 0.80000001 0.80000001
		 0.89999998 0.80000001 1 0.80000001 0.1 0.89999998 0 0.89999998 0.2 0.89999998 0.30000001
		 0.89999998 0.40000001 0.89999998 0.5 0.89999998 0.60000002 0.89999998 0.69999999
		 0.89999998 0.80000001 0.89999998 0.89999998 0.89999998 1 0.89999998 0.1 1 0 1 0.2
		 1 0.30000001 1 0.40000001 1 0.5 1 0.60000002 1 0.69999999 1 0.80000001 1 0.89999998
		 1 1 1;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 121 ".vt[0:120]"  -12 0 12 -9.60000038 0 12 -7.19999981 0 12
		 -4.80000019 0 12 -2.4000001 0 12 0 0 12 2.40000105 0 12 4.80000019 0 12 7.19999981 0 12
		 9.60000134 0 12 12 0 12 -12 0 9.60000038 -9.60000038 0 9.60000038 -7.19999981 0 9.60000038
		 -4.80000019 0 9.60000038 -2.4000001 0 9.60000038 0 0 9.60000038 2.40000105 0 9.60000038
		 4.80000019 0 9.60000038 7.19999981 0 9.60000038 9.60000134 0 9.60000038 12 0 9.60000038
		 -12 0 7.19999981 -9.60000038 0 7.19999981 -7.19999981 0 7.19999981 -4.80000019 0 7.19999981
		 -2.4000001 0 7.19999981 0 0 7.19999981 2.40000105 0 7.19999981 4.80000019 0 7.19999981
		 7.19999981 0 7.19999981 9.60000134 0 7.19999981 12 0 7.19999981 -12 0 4.80000019
		 -9.60000038 0 4.80000019 -7.19999981 0 4.80000019 -4.80000019 0 4.80000019 -2.4000001 0 4.80000019
		 0 0 4.80000019 2.40000105 0 4.80000019 4.80000019 0 4.80000019 7.19999981 0 4.80000019
		 9.60000134 0 4.80000019 12 0 4.80000019 -12 0 2.4000001 -9.60000038 0 2.4000001 -7.19999981 0 2.4000001
		 -4.80000019 0 2.4000001 -2.4000001 0 2.4000001 0 0 2.4000001 2.40000105 0 2.4000001
		 4.80000019 0 2.4000001 7.19999981 0 2.4000001 9.60000134 0 2.4000001 12 0 2.4000001
		 -12 0 0 -9.60000038 0 0 -7.19999981 0 0 -4.80000019 0 0 -2.4000001 0 0 0 0 0 2.40000105 0 0
		 4.80000019 0 0 7.19999981 0 0 9.60000134 0 0 12 0 0 -12 0 -2.40000105 -9.60000038 0 -2.40000105
		 -7.19999981 0 -2.40000105 -4.80000019 0 -2.40000105 -2.4000001 0 -2.40000105 0 0 -2.40000105
		 2.40000105 0 -2.40000105 4.80000019 0 -2.40000105 7.19999981 0 -2.40000105 9.60000134 0 -2.40000105
		 12 0 -2.40000105 -12 0 -4.80000019 -9.60000038 0 -4.80000019 -7.19999981 0 -4.80000019
		 -4.80000019 0 -4.80000019 -2.4000001 0 -4.80000019 0 0 -4.80000019 2.40000105 0 -4.80000019
		 4.80000019 0 -4.80000019 7.19999981 0 -4.80000019 9.60000134 0 -4.80000019 12 0 -4.80000019
		 -12 0 -7.19999981 -9.60000038 0 -7.19999981 -7.19999981 0 -7.19999981 -4.80000019 0 -7.19999981
		 -2.4000001 0 -7.19999981 0 0 -7.19999981 2.40000105 0 -7.19999981 4.80000019 0 -7.19999981
		 7.19999981 0 -7.19999981 9.60000134 0 -7.19999981 12 0 -7.19999981 -12 0 -9.60000134
		 -9.60000038 0 -9.60000134 -7.19999981 0 -9.60000134 -4.80000019 0 -9.60000134 -2.4000001 0 -9.60000134
		 0 0 -9.60000134 2.40000105 0 -9.60000134 4.80000019 0 -9.60000134 7.19999981 0 -9.60000134
		 9.60000134 0 -9.60000134 12 0 -9.60000134 -12 0 -12 -9.60000038 0 -12 -7.19999981 0 -12
		 -4.80000019 0 -12 -2.4000001 0 -12 0 0 -12 2.40000105 0 -12 4.80000019 0 -12 7.19999981 0 -12
		 9.60000134 0 -12 12 0 -12;
	setAttr -s 220 ".ed";
	setAttr ".ed[0:165]"  0 1 0 1 12 0 12 11 0 11 0 0 1 2 0 2 13 0 13 12 0 2 3 0
		 3 14 0 14 13 0 3 4 0 4 15 0 15 14 0 4 5 0 5 16 0 16 15 0 5 6 0 6 17 0 17 16 0 6 7 0
		 7 18 0 18 17 0 7 8 0 8 19 0 19 18 0 8 9 0 9 20 0 20 19 0 9 10 0 10 21 0 21 20 0 12 23 0
		 23 22 0 22 11 0 13 24 0 24 23 0 14 25 0 25 24 0 15 26 0 26 25 0 16 27 0 27 26 0 17 28 0
		 28 27 0 18 29 0 29 28 0 19 30 0 30 29 0 20 31 0 31 30 0 21 32 0 32 31 0 23 34 0 34 33 0
		 33 22 0 24 35 0 35 34 0 25 36 0 36 35 0 26 37 0 37 36 0 27 38 0 38 37 0 28 39 0 39 38 0
		 29 40 0 40 39 0 30 41 0 41 40 0 31 42 0 42 41 0 32 43 0 43 42 0 34 45 0 45 44 0 44 33 0
		 35 46 0 46 45 0 36 47 0 47 46 0 37 48 0 48 47 0 38 49 0 49 48 0 39 50 0 50 49 0 40 51 0
		 51 50 0 41 52 0 52 51 0 42 53 0 53 52 0 43 54 0 54 53 0 45 56 0 56 55 0 55 44 0 46 57 0
		 57 56 0 47 58 0 58 57 0 48 59 0 59 58 0 49 60 0 60 59 0 50 61 0 61 60 0 51 62 0 62 61 0
		 52 63 0 63 62 0 53 64 0 64 63 0 54 65 0 65 64 0 56 67 0 67 66 0 66 55 0 57 68 0 68 67 0
		 58 69 0 69 68 0 59 70 0 70 69 0 60 71 0 71 70 0 61 72 0 72 71 0 62 73 0 73 72 0 63 74 0
		 74 73 0 64 75 0 75 74 0 65 76 0 76 75 0 67 78 0 78 77 0 77 66 0 68 79 0 79 78 0 69 80 0
		 80 79 0 70 81 0 81 80 0 71 82 0 82 81 0 72 83 0 83 82 0 73 84 0 84 83 0 74 85 0 85 84 0
		 75 86 0 86 85 0 76 87 0 87 86 0 78 89 0 89 88 0 88 77 0 79 90 0 90 89 0 80 91 0 91 90 0
		 81 92 0 92 91 0;
	setAttr ".ed[166:219]" 82 93 0 93 92 0 83 94 0 94 93 0 84 95 0 95 94 0 85 96 0
		 96 95 0 86 97 0 97 96 0 87 98 0 98 97 0 89 100 0 100 99 0 99 88 0 90 101 0 101 100 0
		 91 102 0 102 101 0 92 103 0 103 102 0 93 104 0 104 103 0 94 105 0 105 104 0 95 106 0
		 106 105 0 96 107 0 107 106 0 97 108 0 108 107 0 98 109 0 109 108 0 100 111 0 111 110 0
		 110 99 0 101 112 0 112 111 0 102 113 0 113 112 0 103 114 0 114 113 0 104 115 0 115 114 0
		 105 116 0 116 115 0 106 117 0 117 116 0 107 118 0 118 117 0 108 119 0 119 118 0 109 120 0
		 120 119 0;
	setAttr -s 400 ".n";
	setAttr ".n[0:165]" -type "float3"  0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0
		 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0
		 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1
		 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0
		 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0
		 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1
		 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0
		 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0
		 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1
		 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0
		 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0
		 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1
		 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0;
	setAttr ".n[166:331]" -type "float3"  0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0
		 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0
		 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1
		 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0
		 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0
		 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1
		 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0
		 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0
		 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1
		 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0
		 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0
		 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1
		 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0;
	setAttr ".n[332:399]" -type "float3"  0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0
		 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0
		 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1
		 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0
		 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0
		 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0;
	setAttr -s 100 -ch 400 ".fc[0:99]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 4 5 6 -2
		mu 0 4 1 4 5 2
		f 4 7 8 9 -6
		mu 0 4 4 6 7 5
		f 4 10 11 12 -9
		mu 0 4 6 8 9 7
		f 4 13 14 15 -12
		mu 0 4 8 10 11 9
		f 4 16 17 18 -15
		mu 0 4 10 12 13 11
		f 4 19 20 21 -18
		mu 0 4 12 14 15 13
		f 4 22 23 24 -21
		mu 0 4 14 16 17 15
		f 4 25 26 27 -24
		mu 0 4 16 18 19 17
		f 4 28 29 30 -27
		mu 0 4 18 20 21 19
		f 4 -3 31 32 33
		mu 0 4 3 2 22 23
		f 4 -7 34 35 -32
		mu 0 4 2 5 24 22
		f 4 -10 36 37 -35
		mu 0 4 5 7 25 24
		f 4 -13 38 39 -37
		mu 0 4 7 9 26 25
		f 4 -16 40 41 -39
		mu 0 4 9 11 27 26
		f 4 -19 42 43 -41
		mu 0 4 11 13 28 27
		f 4 -22 44 45 -43
		mu 0 4 13 15 29 28
		f 4 -25 46 47 -45
		mu 0 4 15 17 30 29
		f 4 -28 48 49 -47
		mu 0 4 17 19 31 30
		f 4 -31 50 51 -49
		mu 0 4 19 21 32 31
		f 4 -33 52 53 54
		mu 0 4 23 22 33 34
		f 4 -36 55 56 -53
		mu 0 4 22 24 35 33
		f 4 -38 57 58 -56
		mu 0 4 24 25 36 35
		f 4 -40 59 60 -58
		mu 0 4 25 26 37 36
		f 4 -42 61 62 -60
		mu 0 4 26 27 38 37
		f 4 -44 63 64 -62
		mu 0 4 27 28 39 38
		f 4 -46 65 66 -64
		mu 0 4 28 29 40 39
		f 4 -48 67 68 -66
		mu 0 4 29 30 41 40
		f 4 -50 69 70 -68
		mu 0 4 30 31 42 41
		f 4 -52 71 72 -70
		mu 0 4 31 32 43 42
		f 4 -54 73 74 75
		mu 0 4 34 33 44 45
		f 4 -57 76 77 -74
		mu 0 4 33 35 46 44
		f 4 -59 78 79 -77
		mu 0 4 35 36 47 46
		f 4 -61 80 81 -79
		mu 0 4 36 37 48 47
		f 4 -63 82 83 -81
		mu 0 4 37 38 49 48
		f 4 -65 84 85 -83
		mu 0 4 38 39 50 49
		f 4 -67 86 87 -85
		mu 0 4 39 40 51 50
		f 4 -69 88 89 -87
		mu 0 4 40 41 52 51
		f 4 -71 90 91 -89
		mu 0 4 41 42 53 52
		f 4 -73 92 93 -91
		mu 0 4 42 43 54 53
		f 4 -75 94 95 96
		mu 0 4 45 44 55 56
		f 4 -78 97 98 -95
		mu 0 4 44 46 57 55
		f 4 -80 99 100 -98
		mu 0 4 46 47 58 57
		f 4 -82 101 102 -100
		mu 0 4 47 48 59 58
		f 4 -84 103 104 -102
		mu 0 4 48 49 60 59
		f 4 -86 105 106 -104
		mu 0 4 49 50 61 60
		f 4 -88 107 108 -106
		mu 0 4 50 51 62 61
		f 4 -90 109 110 -108
		mu 0 4 51 52 63 62
		f 4 -92 111 112 -110
		mu 0 4 52 53 64 63
		f 4 -94 113 114 -112
		mu 0 4 53 54 65 64
		f 4 -96 115 116 117
		mu 0 4 56 55 66 67
		f 4 -99 118 119 -116
		mu 0 4 55 57 68 66
		f 4 -101 120 121 -119
		mu 0 4 57 58 69 68
		f 4 -103 122 123 -121
		mu 0 4 58 59 70 69
		f 4 -105 124 125 -123
		mu 0 4 59 60 71 70
		f 4 -107 126 127 -125
		mu 0 4 60 61 72 71
		f 4 -109 128 129 -127
		mu 0 4 61 62 73 72
		f 4 -111 130 131 -129
		mu 0 4 62 63 74 73
		f 4 -113 132 133 -131
		mu 0 4 63 64 75 74
		f 4 -115 134 135 -133
		mu 0 4 64 65 76 75
		f 4 -117 136 137 138
		mu 0 4 67 66 77 78
		f 4 -120 139 140 -137
		mu 0 4 66 68 79 77
		f 4 -122 141 142 -140
		mu 0 4 68 69 80 79
		f 4 -124 143 144 -142
		mu 0 4 69 70 81 80
		f 4 -126 145 146 -144
		mu 0 4 70 71 82 81
		f 4 -128 147 148 -146
		mu 0 4 71 72 83 82
		f 4 -130 149 150 -148
		mu 0 4 72 73 84 83
		f 4 -132 151 152 -150
		mu 0 4 73 74 85 84
		f 4 -134 153 154 -152
		mu 0 4 74 75 86 85
		f 4 -136 155 156 -154
		mu 0 4 75 76 87 86
		f 4 -138 157 158 159
		mu 0 4 78 77 88 89
		f 4 -141 160 161 -158
		mu 0 4 77 79 90 88
		f 4 -143 162 163 -161
		mu 0 4 79 80 91 90
		f 4 -145 164 165 -163
		mu 0 4 80 81 92 91
		f 4 -147 166 167 -165
		mu 0 4 81 82 93 92
		f 4 -149 168 169 -167
		mu 0 4 82 83 94 93
		f 4 -151 170 171 -169
		mu 0 4 83 84 95 94
		f 4 -153 172 173 -171
		mu 0 4 84 85 96 95
		f 4 -155 174 175 -173
		mu 0 4 85 86 97 96
		f 4 -157 176 177 -175
		mu 0 4 86 87 98 97
		f 4 -159 178 179 180
		mu 0 4 89 88 99 100
		f 4 -162 181 182 -179
		mu 0 4 88 90 101 99
		f 4 -164 183 184 -182
		mu 0 4 90 91 102 101
		f 4 -166 185 186 -184
		mu 0 4 91 92 103 102
		f 4 -168 187 188 -186
		mu 0 4 92 93 104 103
		f 4 -170 189 190 -188
		mu 0 4 93 94 105 104
		f 4 -172 191 192 -190
		mu 0 4 94 95 106 105
		f 4 -174 193 194 -192
		mu 0 4 95 96 107 106
		f 4 -176 195 196 -194
		mu 0 4 96 97 108 107
		f 4 -178 197 198 -196
		mu 0 4 97 98 109 108
		f 4 -180 199 200 201
		mu 0 4 100 99 110 111
		f 4 -183 202 203 -200
		mu 0 4 99 101 112 110
		f 4 -185 204 205 -203
		mu 0 4 101 102 113 112
		f 4 -187 206 207 -205
		mu 0 4 102 103 114 113
		f 4 -189 208 209 -207
		mu 0 4 103 104 115 114
		f 4 -191 210 211 -209
		mu 0 4 104 105 116 115
		f 4 -193 212 213 -211
		mu 0 4 105 106 117 116
		f 4 -195 214 215 -213
		mu 0 4 106 107 118 117
		f 4 -197 216 217 -215
		mu 0 4 107 108 119 118
		f 4 -199 218 219 -217
		mu 0 4 108 109 120 119;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
createNode transform -n "geom:pSphere1" -p "group1";
	rename -uid "4C1C82D9-4099-3324-80E3-5089CF7DE71E";
createNode mesh -n "geom:pSphere1Shape" -p "geom:pSphere1";
	rename -uid "863CA6E2-439C-D50C-398E-0F966FD2BD74";
	setAttr -k off ".v";
	setAttr ".iog[0].og[0].gcl" -type "componentList" 1 "f[0:399]";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 439 ".uvst[0].uvsp";
	setAttr ".uvst[0].uvsp[0:249]" -type "float2" 0 0.050000001 0.050000001 0.050000001
		 0.050000001 0.1 0 0.1 0.1 0.050000001 0.1 0.1 0.15000001 0.050000001 0.15000001 0.1
		 0.2 0.050000001 0.2 0.1 0.25 0.050000001 0.25 0.1 0.30000001 0.050000001 0.30000001
		 0.1 0.34999999 0.050000001 0.34999999 0.1 0.40000001 0.050000001 0.40000001 0.1 0.44999999
		 0.050000001 0.44999999 0.1 0.5 0.050000001 0.5 0.1 0.55000001 0.050000001 0.55000001
		 0.1 0.60000002 0.050000001 0.60000002 0.1 0.64999998 0.050000001 0.64999998 0.1 0.69999999
		 0.050000001 0.69999999 0.1 0.75 0.050000001 0.75 0.1 0.80000001 0.050000001 0.80000001
		 0.1 0.85000002 0.050000001 0.85000002 0.1 0.89999998 0.050000001 0.89999998 0.1 0.94999999
		 0.050000001 0.94999999 0.1 1 0.050000001 1 0.1 0.050000001 0.15000001 0 0.15000001
		 0.1 0.15000001 0.15000001 0.15000001 0.2 0.15000001 0.25 0.15000001 0.30000001 0.15000001
		 0.34999999 0.15000001 0.40000001 0.15000001 0.44999999 0.15000001 0.5 0.15000001
		 0.55000001 0.15000001 0.60000002 0.15000001 0.64999998 0.15000001 0.69999999 0.15000001
		 0.75 0.15000001 0.80000001 0.15000001 0.85000002 0.15000001 0.89999998 0.15000001
		 0.94999999 0.15000001 1 0.15000001 0.050000001 0.2 0 0.2 0.1 0.2 0.15000001 0.2 0.2
		 0.2 0.25 0.2 0.30000001 0.2 0.34999999 0.2 0.40000001 0.2 0.44999999 0.2 0.5 0.2
		 0.55000001 0.2 0.60000002 0.2 0.64999998 0.2 0.69999999 0.2 0.75 0.2 0.80000001 0.2
		 0.85000002 0.2 0.89999998 0.2 0.94999999 0.2 1 0.2 0.050000001 0.25 0 0.25 0.1 0.25
		 0.15000001 0.25 0.2 0.25 0.25 0.25 0.30000001 0.25 0.34999999 0.25 0.40000001 0.25
		 0.44999999 0.25 0.5 0.25 0.55000001 0.25 0.60000002 0.25 0.64999998 0.25 0.69999999
		 0.25 0.75 0.25 0.80000001 0.25 0.85000002 0.25 0.89999998 0.25 0.94999999 0.25 1
		 0.25 0.050000001 0.30000001 0 0.30000001 0.1 0.30000001 0.15000001 0.30000001 0.2
		 0.30000001 0.25 0.30000001 0.30000001 0.30000001 0.34999999 0.30000001 0.40000001
		 0.30000001 0.44999999 0.30000001 0.5 0.30000001 0.55000001 0.30000001 0.60000002
		 0.30000001 0.64999998 0.30000001 0.69999999 0.30000001 0.75 0.30000001 0.80000001
		 0.30000001 0.85000002 0.30000001 0.89999998 0.30000001 0.94999999 0.30000001 1 0.30000001
		 0.050000001 0.34999999 0 0.34999999 0.1 0.34999999 0.15000001 0.34999999 0.2 0.34999999
		 0.25 0.34999999 0.30000001 0.34999999 0.34999999 0.34999999 0.40000001 0.34999999
		 0.44999999 0.34999999 0.5 0.34999999 0.55000001 0.34999999 0.60000002 0.34999999
		 0.64999998 0.34999999 0.69999999 0.34999999 0.75 0.34999999 0.80000001 0.34999999
		 0.85000002 0.34999999 0.89999998 0.34999999 0.94999999 0.34999999 1 0.34999999 0.050000001
		 0.40000001 0 0.40000001 0.1 0.40000001 0.15000001 0.40000001 0.2 0.40000001 0.25
		 0.40000001 0.30000001 0.40000001 0.34999999 0.40000001 0.40000001 0.40000001 0.44999999
		 0.40000001 0.5 0.40000001 0.55000001 0.40000001 0.60000002 0.40000001 0.64999998
		 0.40000001 0.69999999 0.40000001 0.75 0.40000001 0.80000001 0.40000001 0.85000002
		 0.40000001 0.89999998 0.40000001 0.94999999 0.40000001 1 0.40000001 0.050000001 0.44999999
		 0 0.44999999 0.1 0.44999999 0.15000001 0.44999999 0.2 0.44999999 0.25 0.44999999
		 0.30000001 0.44999999 0.34999999 0.44999999 0.40000001 0.44999999 0.44999999 0.44999999
		 0.5 0.44999999 0.55000001 0.44999999 0.60000002 0.44999999 0.64999998 0.44999999
		 0.69999999 0.44999999 0.75 0.44999999 0.80000001 0.44999999 0.85000002 0.44999999
		 0.89999998 0.44999999 0.94999999 0.44999999 1 0.44999999 0.050000001 0.5 0 0.5 0.1
		 0.5 0.15000001 0.5 0.2 0.5 0.25 0.5 0.30000001 0.5 0.34999999 0.5 0.40000001 0.5
		 0.44999999 0.5 0.5 0.5 0.55000001 0.5 0.60000002 0.5 0.64999998 0.5 0.69999999 0.5
		 0.75 0.5 0.80000001 0.5 0.85000002 0.5 0.89999998 0.5 0.94999999 0.5 1 0.5 0.050000001
		 0.55000001 0 0.55000001 0.1 0.55000001 0.15000001 0.55000001 0.2 0.55000001 0.25
		 0.55000001 0.30000001 0.55000001 0.34999999 0.55000001 0.40000001 0.55000001 0.44999999
		 0.55000001 0.5 0.55000001 0.55000001 0.55000001 0.60000002 0.55000001 0.64999998
		 0.55000001 0.69999999 0.55000001 0.75 0.55000001 0.80000001 0.55000001 0.85000002
		 0.55000001 0.89999998 0.55000001 0.94999999 0.55000001 1 0.55000001 0.050000001 0.60000002
		 0 0.60000002 0.1 0.60000002 0.15000001 0.60000002 0.2 0.60000002 0.25 0.60000002
		 0.30000001 0.60000002 0.34999999 0.60000002 0.40000001 0.60000002 0.44999999 0.60000002
		 0.5 0.60000002 0.55000001 0.60000002 0.60000002 0.60000002 0.64999998 0.60000002
		 0.69999999 0.60000002 0.75 0.60000002 0.80000001 0.60000002 0.85000002 0.60000002
		 0.89999998 0.60000002;
	setAttr ".uvst[0].uvsp[250:438]" 0.94999999 0.60000002 1 0.60000002 0.050000001
		 0.64999998 0 0.64999998 0.1 0.64999998 0.15000001 0.64999998 0.2 0.64999998 0.25
		 0.64999998 0.30000001 0.64999998 0.34999999 0.64999998 0.40000001 0.64999998 0.44999999
		 0.64999998 0.5 0.64999998 0.55000001 0.64999998 0.60000002 0.64999998 0.64999998
		 0.64999998 0.69999999 0.64999998 0.75 0.64999998 0.80000001 0.64999998 0.85000002
		 0.64999998 0.89999998 0.64999998 0.94999999 0.64999998 1 0.64999998 0.050000001 0.69999999
		 0 0.69999999 0.1 0.69999999 0.15000001 0.69999999 0.2 0.69999999 0.25 0.69999999
		 0.30000001 0.69999999 0.34999999 0.69999999 0.40000001 0.69999999 0.44999999 0.69999999
		 0.5 0.69999999 0.55000001 0.69999999 0.60000002 0.69999999 0.64999998 0.69999999
		 0.69999999 0.69999999 0.75 0.69999999 0.80000001 0.69999999 0.85000002 0.69999999
		 0.89999998 0.69999999 0.94999999 0.69999999 1 0.69999999 0.050000001 0.75 0 0.75
		 0.1 0.75 0.15000001 0.75 0.2 0.75 0.25 0.75 0.30000001 0.75 0.34999999 0.75 0.40000001
		 0.75 0.44999999 0.75 0.5 0.75 0.55000001 0.75 0.60000002 0.75 0.64999998 0.75 0.69999999
		 0.75 0.75 0.75 0.80000001 0.75 0.85000002 0.75 0.89999998 0.75 0.94999999 0.75 1
		 0.75 0.050000001 0.80000001 0 0.80000001 0.1 0.80000001 0.15000001 0.80000001 0.2
		 0.80000001 0.25 0.80000001 0.30000001 0.80000001 0.34999999 0.80000001 0.40000001
		 0.80000001 0.44999999 0.80000001 0.5 0.80000001 0.55000001 0.80000001 0.60000002
		 0.80000001 0.64999998 0.80000001 0.69999999 0.80000001 0.75 0.80000001 0.80000001
		 0.80000001 0.85000002 0.80000001 0.89999998 0.80000001 0.94999999 0.80000001 1 0.80000001
		 0.050000001 0.85000002 0 0.85000002 0.1 0.85000002 0.15000001 0.85000002 0.2 0.85000002
		 0.25 0.85000002 0.30000001 0.85000002 0.34999999 0.85000002 0.40000001 0.85000002
		 0.44999999 0.85000002 0.5 0.85000002 0.55000001 0.85000002 0.60000002 0.85000002
		 0.64999998 0.85000002 0.69999999 0.85000002 0.75 0.85000002 0.80000001 0.85000002
		 0.85000002 0.85000002 0.89999998 0.85000002 0.94999999 0.85000002 1 0.85000002 0.050000001
		 0.89999998 0 0.89999998 0.1 0.89999998 0.15000001 0.89999998 0.2 0.89999998 0.25
		 0.89999998 0.30000001 0.89999998 0.34999999 0.89999998 0.40000001 0.89999998 0.44999999
		 0.89999998 0.5 0.89999998 0.55000001 0.89999998 0.60000002 0.89999998 0.64999998
		 0.89999998 0.69999999 0.89999998 0.75 0.89999998 0.80000001 0.89999998 0.85000002
		 0.89999998 0.89999998 0.89999998 0.94999999 0.89999998 1 0.89999998 0.050000001 0.94999999
		 0 0.94999999 0.1 0.94999999 0.15000001 0.94999999 0.2 0.94999999 0.25 0.94999999
		 0.30000001 0.94999999 0.34999999 0.94999999 0.40000001 0.94999999 0.44999999 0.94999999
		 0.5 0.94999999 0.55000001 0.94999999 0.60000002 0.94999999 0.64999998 0.94999999
		 0.69999999 0.94999999 0.75 0.94999999 0.80000001 0.94999999 0.85000002 0.94999999
		 0.89999998 0.94999999 0.94999999 0.94999999 1 0.94999999 0.025 0 0.075000003 0 0.125
		 0 0.175 0 0.22499999 0 0.27500001 0 0.32499999 0 0.375 0 0.42500001 0 0.47499999
		 0 0.52499998 0 0.57499999 0 0.625 0 0.67500001 0 0.72500002 0 0.77499998 0 0.82499999
		 0 0.875 0 0.92500001 0 0.97500002 0 0.025 1 0.075000003 1 0.125 1 0.175 1 0.22499999
		 1 0.27500001 1 0.32499999 1 0.375 1 0.42500001 1 0.47499999 1 0.52499998 1 0.57499999
		 1 0.625 1 0.67500001 1 0.72500002 1 0.77499998 1 0.82499999 1 0.875 1 0.92500001
		 1 0.97500002 1;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 382 ".vt";
	setAttr ".vt[0:165]"  -4.9075489 0.064745001 7.47408485 -4.9456358 0.100474 7.38523102
		 -5.0099539757 0.13957199 7.31482697 -5.09420681 0.178213 7.2697649 -5.19014597 0.212613 7.25445414
		 -5.28838205 0.23940501 7.2703948 -5.37929821 0.255968 7.31602621 -5.4539938 0.26067799 7.38688087
		 -5.5051589 0.253077 7.47602415 -5.52778387 0.233907 7.57472992 -5.51965618 0.205045 7.67333603
		 -5.48156786 0.16931599 7.76218891 -5.41725016 0.130218 7.83259296 -5.3329978 0.091577001 7.87765598
		 -5.23705816 0.057177 7.89296722 -5.13882303 0.030385001 7.87702608 -5.047906876 0.013822 7.83139515
		 -4.97321081 0.0091110002 7.76054001 -4.92204618 0.016713001 7.67139578 -4.89941978 0.035882998 7.57269096
		 -4.58650494 0.067607999 7.39592123 -4.66174221 0.13818599 7.22040176 -4.78879404 0.21541999 7.081326962
		 -4.95522404 0.291749 6.992311 -5.14474106 0.35970199 6.96206713 -5.33879423 0.41262701 6.99355602
		 -5.51838589 0.445344 7.083694935 -5.66593981 0.45465001 7.22366095 -5.76701021 0.439634 7.39975214
		 -5.81170416 0.401766 7.59473324 -5.79564619 0.34475201 7.78951597 -5.72040892 0.274174 7.96503496
		 -5.59335709 0.19694 8.10410976 -5.42692709 0.120611 8.19312572 -5.23741007 0.052657999 8.2233696
		 -5.043357849 -0.000267 8.19188118 -4.86376476 -0.032984 8.10174179 -4.7162118 -0.042289998 7.96177721
		 -4.61514187 -0.027274 7.78568506 -4.57044792 0.010594 7.59070492 -4.26594687 0.119454 7.33475494
		 -4.37648106 0.223143 7.076891899 -4.56313896 0.336611 6.87257099 -4.80764818 0.44874999 6.74179411
		 -5.086075783 0.54858297 6.69736099 -5.37116718 0.62633801 6.74362183 -5.63501501 0.67440301 6.87604904
		 -5.85179186 0.68807501 7.081678867 -6.00027799606 0.66601402 7.34038305 -6.065939903 0.61037999 7.62683821
		 -6.042348862 0.52661902 7.91300201 -5.93181515 0.42293 8.17086601 -5.7451582 0.30946201 8.37518597
		 -5.50064802 0.19732399 8.50596333 -5.2222209 0.097491004 8.55039597 -4.93712997 0.019735999 8.50413513
		 -4.67328215 -0.02833 8.37170792 -4.45650482 -0.042002 8.16607761 -4.30801821 -0.019941 7.90737391
		 -4.24235678 0.035693001 7.62092018 -3.95376801 0.219007 7.29209185 -4.096877098 0.353255 6.95823383
		 -4.33854389 0.50016201 6.69369888 -4.65511322 0.64534903 6.52438021 -5.015594959 0.77460301 6.46685314
		 -5.38470507 0.87527299 6.52674818 -5.72631121 0.93750501 6.69820213 -6.0069742203 0.95520502 6.96443319
		 -6.19922113 0.92664301 7.29937887 -6.28423405 0.85461301 7.67025423 -6.25368977 0.746167 8.040754318
		 -6.11058092 0.61192 8.37461185 -5.86891413 0.46501201 8.6391468 -5.5523448 0.31982601 8.808465
		 -5.19186306 0.190571 8.86599255 -4.82275391 0.089901 8.80609798 -4.48114777 0.02767 8.63464355
		 -4.20048523 0.0099689998 8.36841297 -4.0082378387 0.038532 8.033467293 -3.92322493 0.110561 7.66259193
		 -3.65765405 0.36381599 7.26898384 -3.82981491 0.525316 6.86735201 -4.1205411 0.70204598 6.54911518
		 -4.50137377 0.876706 6.34542513 -4.93503523 1.032199025 6.27621889 -5.3790741 1.15330601 6.3482728
		 -5.79002714 1.22817004 6.554533 -6.12766504 1.24946404 6.87480879 -6.35893822 1.21510303 7.27775002
		 -6.46120882 1.12845099 7.72391319 -6.42446613 0.99799001 8.16962528 -6.25230503 0.83648998 8.57125568
		 -5.96157885 0.65976101 8.88949299 -5.58074617 0.48510101 9.093182564 -5.14708519 0.32960701 9.1623888
		 -4.70304585 0.208501 9.090334892 -4.29209423 0.133637 8.88407516 -3.95445609 0.112343 8.56379986
		 -3.72318196 0.146704 8.16085911 -3.62091088 0.233356 7.71469593 -3.38489699 0.55031502 7.26599789
		 -3.58187103 0.73509097 6.80648184 -3.9144969 0.93729103 6.44237995 -4.35021687 1.13712394 6.2093339
		 -4.84637785 1.315027 6.13015413 -5.35441399 1.45358801 6.21259212 -5.82459402 1.53924203 6.44857883
		 -6.21089315 1.563604 6.81501389 -6.47549915 1.52429199 7.27602816 -6.59250879 1.42515099 7.78649282
		 -6.55046988 1.27588797 8.29644203 -6.35349607 1.091112018 8.7559576 -6.020870209 0.88891202 9.12005997
		 -5.5851512 0.68907899 9.35310745 -5.088990211 0.51117599 9.43228626 -4.58095407 0.37261501 9.34984779
		 -4.11077404 0.286962 9.11386108 -3.72447491 0.26259899 8.74742699 -3.45986891 0.30191201 8.28641319
		 -3.34285903 0.401052 7.77594805 -3.14221406 0.77391201 7.28320885 -3.35914898 0.977413 6.77712393
		 -3.72548604 1.20010602 6.376122 -4.2053628 1.42018998 6.11945677 -4.75180817 1.61612296 6.032252789
		 -5.31132984 1.76872599 6.12304592 -5.82916021 1.86306 6.38294888 -6.25460911 1.88989198 6.78652
		 -6.546031 1.84659505 7.29425478 -6.67490005 1.73740804 7.8564539 -6.62860012 1.573017 8.41808414
		 -6.41166496 1.36951602 8.92416859 -6.045329094 1.14682305 9.32516956 -5.56545115 0.92673898 9.58183479
		 -5.019007206 0.73080599 9.66903877 -4.45948505 0.57820302 9.57824612 -3.94165492 0.48386899 9.31834412
		 -3.51620603 0.457037 8.91477299 -3.2247839 0.50033402 8.40703773 -3.095916033 0.60952097 7.84484005
		 -2.93558002 1.029099941 7.32019281 -3.16713595 1.24631703 6.78000021 -3.55816102 1.48401797 6.3519721
		 -4.070380211 1.71893501 6.078010082 -4.65365314 1.92807305 5.98492813 -5.25088501 2.090960979 6.081840038
		 -5.80361509 2.19165301 6.35925913 -6.25773716 2.22029305 6.79002905 -6.56879902 2.17407799 7.33198404
		 -6.70635319 2.057532072 7.93207216 -6.65693283 1.88206196 8.53155327 -6.42537689 1.66484499 9.071746826
		 -6.034350872 1.427145 9.49977398 -5.52213287 1.19222701 9.77373695 -4.93885994 0.98308903 9.86681843
		 -4.34162807 0.82020199 9.76990604 -3.78889894 0.71951002 9.49248695 -3.33477712 0.69086897 9.061717033
		 -3.023714066 0.73708397 8.51976299 -2.88616109 0.85363102 7.91967487 -2.770082 1.30959702 7.37603998
		 -3.010556936 1.53518105 6.81503916 -3.4166441 1.78203702 6.37052584 -3.94859195 2.026002884 6.086010933
		 -4.55433083 2.24319601 5.98934412 -5.17456579 2.41235805 6.089989185;
	setAttr ".vt[166:331]" -5.74858522 2.51692796 6.37809277 -6.22019911 2.54667211 6.82545519
		 -6.54324198 2.49867606 7.38828421 -6.68609381 2.37764096 8.011486053 -6.63477087 2.19541311 8.63405704
		 -6.39429617 1.96983004 9.19505692 -5.98820877 1.72297299 9.63957119 -5.45626116 1.47900796 9.92408562
		 -4.85052299 1.261814 10.020751953 -4.23028803 1.092653036 9.92010689 -3.65626907 0.98808199 9.63200283
		 -3.18465495 0.95833898 9.18464184 -2.86161089 1.0063339472 8.62181282 -2.71876001 1.12737 7.99861193
		 -2.64979601 1.60849595 7.44937277 -2.89326906 1.83689106 6.88138008 -3.30441809 2.08682394 6.43132496
		 -3.84299707 2.33383107 6.14326286 -4.45628595 2.55373192 6.045392036 -5.084252834 2.72500205 6.14729214
		 -5.66542721 2.83087611 6.43898678 -6.14291906 2.86099005 6.89192486 -6.46998978 2.812397 7.46177006
		 -6.61462212 2.68985295 8.092740059 -6.56265879 2.50535297 8.72307205 -6.31918716 2.27695799 9.29106522
		 -5.90803814 2.027024984 9.74111938 -5.36945915 1.78001797 10.029180527 -4.7561698 1.56011701 10.12705231
		 -4.12820387 1.38884699 10.02515316 -3.54702997 1.28297305 9.73345661 -3.069536924 1.252859 9.28051853
		 -2.74246693 1.30145204 8.71067524 -2.59783506 1.42399704 8.079705238 -2.57768512 1.91843605 7.53838682
		 -2.81816006 2.14401889 6.97738695 -3.22424603 2.39087605 6.53287411 -3.75619507 2.63484097 6.24835777
		 -4.36193323 2.85203505 6.15169191 -4.98216915 3.021197081 6.25233698 -5.55618811 3.12576699 6.54044104
		 -6.027801037 3.15550995 6.98780298 -6.35084486 3.1075151 7.550632 -6.49369717 2.98648 8.17383289
		 -6.4423728 2.80425096 8.79640484 -6.20189905 2.57866812 9.35740471 -5.79581213 2.3318119 9.80191803
		 -5.26386404 2.087846994 10.086434364 -4.65812588 1.87065303 10.18309975 -4.037889957 1.70149195 10.082454681
		 -3.46387196 1.59692097 9.79435062 -2.99225807 1.56717801 9.34698868 -2.66921401 1.61517298 8.78416061
		 -2.5263629 1.73620796 8.16095924 -2.55552197 2.23178697 7.64089203 -2.7870779 2.44900298 7.10069799
		 -3.17810392 2.68670392 6.67267084 -3.69032311 2.92162204 6.39870787 -4.27359581 3.13075995 6.30562687
		 -4.87082815 3.293648 6.40253878 -5.42355824 3.39434004 6.67995691 -5.87767982 3.42298007 7.11072683
		 -6.18874216 3.37676501 7.65268183 -6.32629585 3.26021791 8.25277042 -6.27687597 3.084748983 8.85225105
		 -6.045320034 2.86753201 9.39244461 -5.65429401 2.62983108 9.82047176 -5.14207602 2.39491391 10.094434738
		 -4.55880308 2.185776 10.18751621 -3.96157098 2.022887945 10.090603828 -3.40884209 1.92219603 9.81318474
		 -2.95472002 1.893556 9.38241482 -2.64365697 1.93977106 8.84046078 -2.50610399 2.056318045 8.24037266
		 -2.58385491 2.54083204 7.75436115 -2.80079103 2.74433303 7.24827623 -3.16712689 2.967026 6.84727383
		 -3.64700508 3.18710995 6.59060907 -4.19344902 3.38304305 6.50340509 -4.75297213 3.53564596 6.59419823
		 -5.27080202 3.62998104 6.85410118 -5.69625092 3.65681195 7.25767183 -5.98767185 3.6135149 7.76540709
		 -6.11654091 3.50432801 8.32760525 -6.070240974 3.33993697 8.88923454 -5.85330582 3.13643599 9.39532089
		 -5.48696995 2.91374397 9.79632187 -5.0070929527 2.69365907 10.052987099 -4.46064806 2.49772596 10.14019108
		 -3.90112591 2.34512305 10.049398422 -3.38329601 2.25078893 9.78949642 -2.95784712 2.22395706 9.38592529
		 -2.66642499 2.26725411 8.87819004 -2.53755689 2.37644196 8.3159914 -2.66198611 2.83796096 7.87600183
		 -2.85895896 3.022737026 7.41648579 -3.19158602 3.22493696 7.0523839 -3.62730503 3.42477012 6.81933784
		 -4.12346697 3.60267305 6.74015808 -4.63150215 3.74123406 6.82259703 -5.10168219 3.82688808 7.058582783
		 -5.4879818 3.85124993 7.42501783 -5.75258684 3.81193805 7.8860321 -5.86959696 3.71279693 8.39649677
		 -5.82755804 3.56353402 8.90644741 -5.63058519 3.37875795 9.36596203 -5.29795885 3.17655802 9.73006439
		 -4.86223888 2.9767251 9.96311092 -4.3660779 2.79882193 10.042289734 -3.85804296 2.66026092 9.95985222
		 -3.38786292 2.57460809 9.72386646 -3.0015630722 2.55024505 9.35743141 -2.73695803 2.58955789 8.89641666
		 -2.61994791 2.68869805 8.385952 -2.78799009 3.11585903 8.002820015 -2.96015096 3.27735901 7.60118818
		 -3.2508769 3.45408797 7.28295088 -3.63171005 3.62874794 7.079260826 -4.065371037 3.78424191 7.010056019
		 -4.50941086 3.90534806 7.082108974 -4.92036295 3.98021197 7.28836918 -5.25800085 4.0015058517 7.60864496
		 -5.48927498 3.96714497 8.011586189 -5.5915451 3.88049412 8.45774937 -5.55480194 3.7500329 8.90346146
		 -5.38264084 3.58853292 9.30509281 -5.091915131 3.41180301 9.62332916 -4.71108198 3.23714304 9.82701874
		 -4.277421 3.081650019 9.89622498 -3.83338189 2.96054411 9.82417107 -3.42243004 2.88567901 9.61791229
		 -3.084791899 2.86438489 9.29763603 -2.85351801 2.89874601 8.89469528 -2.75124693 2.98539805 8.4485321
		 -2.95876503 3.36768198 8.13169098 -3.10187507 3.50192904 7.79783297 -3.3435421 3.64883709 7.53329802
		 -3.66011095 3.79402304 7.36397886 -4.020593166 3.92327809 7.3064518 -4.3897028 4.023948193 7.36634684
		 -4.73130798 4.08617878 7.53780079 -5.011970997 4.10387993 7.80403185 -5.20421791 4.075316906 8.138978
		 -5.28923082 4.0032877922 8.50985336 -5.25868797 3.89484096 8.88035297 -5.11557913 3.76059389 9.21420956
		 -4.87391186 3.61368704 9.47874641 -4.55734301 3.4684999 9.64806366 -4.19686079 3.33924603 9.7055912
		 -3.82775092 3.23857594 9.64569569 -3.48614597 3.17634511 9.47424221 -3.20548296 3.15864396 9.20801163
		 -3.013236046 3.18720603 8.87306595 -2.92822289 3.2592361 8.50219059 -3.17010593 3.58722997 8.25944328
		 -3.28064108 3.69091892 8.0015792847 -3.46729803 3.80438709 7.79725885 -3.71180797 3.91652489 7.66648102
		 -3.99023509 4.016357899 7.62204885 -4.27532578 4.094112873 7.66831017 -4.53917408 4.14217901 7.8007369
		 -4.75595093 4.15585089 8.0063667297 -4.90443802 4.13379002 8.26507092 -4.97009993 4.078155994 8.55152512
		 -4.94650888 3.99439502 8.83769035 -4.83597517 3.89070606 9.095553398;
	setAttr ".vt[332:381]" -4.64931679 3.77723789 9.29987431 -4.40480804 3.6651001 9.43065071
		 -4.12637997 3.56526709 9.4750843 -3.84128904 3.48751211 9.42882156 -3.57744193 3.43944597 9.2963953
		 -3.36066508 3.4257741 9.090765953 -3.21217799 3.44783497 8.83206177 -3.14651608 3.50346899 8.54560661
		 -3.41681004 3.76909709 8.38292885 -3.49204707 3.83967495 8.20740891 -3.6190989 3.91690898 8.068334579
		 -3.7855289 3.99323797 7.9793191 -3.97504592 4.061191082 7.94907522 -4.1690979 4.11411619 7.98056412
		 -4.34869099 4.14683294 8.070702553 -4.49624395 4.1561389 8.21066761 -4.59731388 4.14112282 8.38675976
		 -4.64200783 4.1032548 8.58174038 -4.62595081 4.046240807 8.77652359 -4.55071402 3.97566295 8.95204258
		 -4.42366219 3.89842892 9.091116905 -4.25723219 3.82209992 9.18013287 -4.067715168 3.75414705 9.21037674
		 -3.87366295 3.70122194 9.17888927 -3.6940701 3.66850495 9.088749886 -3.5465169 3.659199 8.94878387
		 -3.44544601 3.67421508 8.77269268 -3.40075302 3.71208405 8.57771206 -3.69280005 3.90880394 8.49910927
		 -3.73088789 3.94453311 8.41025639 -3.79520607 3.98363209 8.33985233 -3.87945795 4.02227211 8.29478931
		 -3.97539806 4.056672096 8.27947807 -4.073633194 4.083465099 8.29541874 -4.16454887 4.10002708 8.34105015
		 -4.23924494 4.10473824 8.41190529 -4.29041004 4.097136021 8.50104904 -4.31303596 4.077966213 8.59975433
		 -4.30490685 4.049104214 8.69836044 -4.26681995 4.013374805 8.78721333 -4.20250177 3.97427702 8.85761738
		 -4.11824894 3.93563604 8.9026804 -4.02230978 3.90123606 8.91799068 -3.92407393 3.87444401 8.90205002
		 -3.83315897 3.85788107 8.85641861 -3.75846195 3.85317111 8.78556442 -3.70729709 3.86077189 8.69641972
		 -3.68467212 3.87994194 8.59771538 -5.22117281 0.110937 7.56732178 -3.99128294 4.0029120445 8.60512257;
	setAttr -s 780 ".ed";
	setAttr ".ed[0:165]"  0 1 0 1 21 0 21 20 0 20 0 0 1 2 0 2 22 0 22 21 0 2 3 0
		 3 23 0 23 22 0 3 4 0 4 24 0 24 23 0 4 5 0 5 25 0 25 24 0 5 6 0 6 26 0 26 25 0 6 7 0
		 7 27 0 27 26 0 7 8 0 8 28 0 28 27 0 8 9 0 9 29 0 29 28 0 9 10 0 10 30 0 30 29 0 10 11 0
		 11 31 0 31 30 0 11 12 0 12 32 0 32 31 0 12 13 0 13 33 0 33 32 0 13 14 0 14 34 0 34 33 0
		 14 15 0 15 35 0 35 34 0 15 16 0 16 36 0 36 35 0 16 17 0 17 37 0 37 36 0 17 18 0 18 38 0
		 38 37 0 18 19 0 19 39 0 39 38 0 19 0 0 20 39 0 21 41 0 41 40 0 40 20 0 22 42 0 42 41 0
		 23 43 0 43 42 0 24 44 0 44 43 0 25 45 0 45 44 0 26 46 0 46 45 0 27 47 0 47 46 0 28 48 0
		 48 47 0 29 49 0 49 48 0 30 50 0 50 49 0 31 51 0 51 50 0 32 52 0 52 51 0 33 53 0 53 52 0
		 34 54 0 54 53 0 35 55 0 55 54 0 36 56 0 56 55 0 37 57 0 57 56 0 38 58 0 58 57 0 39 59 0
		 59 58 0 40 59 0 41 61 0 61 60 0 60 40 0 42 62 0 62 61 0 43 63 0 63 62 0 44 64 0 64 63 0
		 45 65 0 65 64 0 46 66 0 66 65 0 47 67 0 67 66 0 48 68 0 68 67 0 49 69 0 69 68 0 50 70 0
		 70 69 0 51 71 0 71 70 0 52 72 0 72 71 0 53 73 0 73 72 0 54 74 0 74 73 0 55 75 0 75 74 0
		 56 76 0 76 75 0 57 77 0 77 76 0 58 78 0 78 77 0 59 79 0 79 78 0 60 79 0 61 81 0 81 80 0
		 80 60 0 62 82 0 82 81 0 63 83 0 83 82 0 64 84 0 84 83 0 65 85 0 85 84 0 66 86 0 86 85 0
		 67 87 0 87 86 0 68 88 0 88 87 0 69 89 0 89 88 0 70 90 0 90 89 0 71 91 0 91 90 0 72 92 0
		 92 91 0 73 93 0;
	setAttr ".ed[166:331]" 93 92 0 74 94 0 94 93 0 75 95 0 95 94 0 76 96 0 96 95 0
		 77 97 0 97 96 0 78 98 0 98 97 0 79 99 0 99 98 0 80 99 0 81 101 0 101 100 0 100 80 0
		 82 102 0 102 101 0 83 103 0 103 102 0 84 104 0 104 103 0 85 105 0 105 104 0 86 106 0
		 106 105 0 87 107 0 107 106 0 88 108 0 108 107 0 89 109 0 109 108 0 90 110 0 110 109 0
		 91 111 0 111 110 0 92 112 0 112 111 0 93 113 0 113 112 0 94 114 0 114 113 0 95 115 0
		 115 114 0 96 116 0 116 115 0 97 117 0 117 116 0 98 118 0 118 117 0 99 119 0 119 118 0
		 100 119 0 101 121 0 121 120 0 120 100 0 102 122 0 122 121 0 103 123 0 123 122 0 104 124 0
		 124 123 0 105 125 0 125 124 0 106 126 0 126 125 0 107 127 0 127 126 0 108 128 0 128 127 0
		 109 129 0 129 128 0 110 130 0 130 129 0 111 131 0 131 130 0 112 132 0 132 131 0 113 133 0
		 133 132 0 114 134 0 134 133 0 115 135 0 135 134 0 116 136 0 136 135 0 117 137 0 137 136 0
		 118 138 0 138 137 0 119 139 0 139 138 0 120 139 0 121 141 0 141 140 0 140 120 0 122 142 0
		 142 141 0 123 143 0 143 142 0 124 144 0 144 143 0 125 145 0 145 144 0 126 146 0 146 145 0
		 127 147 0 147 146 0 128 148 0 148 147 0 129 149 0 149 148 0 130 150 0 150 149 0 131 151 0
		 151 150 0 132 152 0 152 151 0 133 153 0 153 152 0 134 154 0 154 153 0 135 155 0 155 154 0
		 136 156 0 156 155 0 137 157 0 157 156 0 138 158 0 158 157 0 139 159 0 159 158 0 140 159 0
		 141 161 0 161 160 0 160 140 0 142 162 0 162 161 0 143 163 0 163 162 0 144 164 0 164 163 0
		 145 165 0 165 164 0 146 166 0 166 165 0 147 167 0 167 166 0 148 168 0 168 167 0 149 169 0
		 169 168 0 150 170 0 170 169 0 151 171 0 171 170 0 152 172 0 172 171 0 153 173 0 173 172 0
		 154 174 0 174 173 0 155 175 0 175 174 0 156 176 0;
	setAttr ".ed[332:497]" 176 175 0 157 177 0 177 176 0 158 178 0 178 177 0 159 179 0
		 179 178 0 160 179 0 161 181 0 181 180 0 180 160 0 162 182 0 182 181 0 163 183 0 183 182 0
		 164 184 0 184 183 0 165 185 0 185 184 0 166 186 0 186 185 0 167 187 0 187 186 0 168 188 0
		 188 187 0 169 189 0 189 188 0 170 190 0 190 189 0 171 191 0 191 190 0 172 192 0 192 191 0
		 173 193 0 193 192 0 174 194 0 194 193 0 175 195 0 195 194 0 176 196 0 196 195 0 177 197 0
		 197 196 0 178 198 0 198 197 0 179 199 0 199 198 0 180 199 0 181 201 0 201 200 0 200 180 0
		 182 202 0 202 201 0 183 203 0 203 202 0 184 204 0 204 203 0 185 205 0 205 204 0 186 206 0
		 206 205 0 187 207 0 207 206 0 188 208 0 208 207 0 189 209 0 209 208 0 190 210 0 210 209 0
		 191 211 0 211 210 0 192 212 0 212 211 0 193 213 0 213 212 0 194 214 0 214 213 0 195 215 0
		 215 214 0 196 216 0 216 215 0 197 217 0 217 216 0 198 218 0 218 217 0 199 219 0 219 218 0
		 200 219 0 201 221 0 221 220 0 220 200 0 202 222 0 222 221 0 203 223 0 223 222 0 204 224 0
		 224 223 0 205 225 0 225 224 0 206 226 0 226 225 0 207 227 0 227 226 0 208 228 0 228 227 0
		 209 229 0 229 228 0 210 230 0 230 229 0 211 231 0 231 230 0 212 232 0 232 231 0 213 233 0
		 233 232 0 214 234 0 234 233 0 215 235 0 235 234 0 216 236 0 236 235 0 217 237 0 237 236 0
		 218 238 0 238 237 0 219 239 0 239 238 0 220 239 0 221 241 0 241 240 0 240 220 0 222 242 0
		 242 241 0 223 243 0 243 242 0 224 244 0 244 243 0 225 245 0 245 244 0 226 246 0 246 245 0
		 227 247 0 247 246 0 228 248 0 248 247 0 229 249 0 249 248 0 230 250 0 250 249 0 231 251 0
		 251 250 0 232 252 0 252 251 0 233 253 0 253 252 0 234 254 0 254 253 0 235 255 0 255 254 0
		 236 256 0 256 255 0 237 257 0 257 256 0 238 258 0 258 257 0 239 259 0;
	setAttr ".ed[498:663]" 259 258 0 240 259 0 241 261 0 261 260 0 260 240 0 242 262 0
		 262 261 0 243 263 0 263 262 0 244 264 0 264 263 0 245 265 0 265 264 0 246 266 0 266 265 0
		 247 267 0 267 266 0 248 268 0 268 267 0 249 269 0 269 268 0 250 270 0 270 269 0 251 271 0
		 271 270 0 252 272 0 272 271 0 253 273 0 273 272 0 254 274 0 274 273 0 255 275 0 275 274 0
		 256 276 0 276 275 0 257 277 0 277 276 0 258 278 0 278 277 0 259 279 0 279 278 0 260 279 0
		 261 281 0 281 280 0 280 260 0 262 282 0 282 281 0 263 283 0 283 282 0 264 284 0 284 283 0
		 265 285 0 285 284 0 266 286 0 286 285 0 267 287 0 287 286 0 268 288 0 288 287 0 269 289 0
		 289 288 0 270 290 0 290 289 0 271 291 0 291 290 0 272 292 0 292 291 0 273 293 0 293 292 0
		 274 294 0 294 293 0 275 295 0 295 294 0 276 296 0 296 295 0 277 297 0 297 296 0 278 298 0
		 298 297 0 279 299 0 299 298 0 280 299 0 281 301 0 301 300 0 300 280 0 282 302 0 302 301 0
		 283 303 0 303 302 0 284 304 0 304 303 0 285 305 0 305 304 0 286 306 0 306 305 0 287 307 0
		 307 306 0 288 308 0 308 307 0 289 309 0 309 308 0 290 310 0 310 309 0 291 311 0 311 310 0
		 292 312 0 312 311 0 293 313 0 313 312 0 294 314 0 314 313 0 295 315 0 315 314 0 296 316 0
		 316 315 0 297 317 0 317 316 0 298 318 0 318 317 0 299 319 0 319 318 0 300 319 0 301 321 0
		 321 320 0 320 300 0 302 322 0 322 321 0 303 323 0 323 322 0 304 324 0 324 323 0 305 325 0
		 325 324 0 306 326 0 326 325 0 307 327 0 327 326 0 308 328 0 328 327 0 309 329 0 329 328 0
		 310 330 0 330 329 0 311 331 0 331 330 0 312 332 0 332 331 0 313 333 0 333 332 0 314 334 0
		 334 333 0 315 335 0 335 334 0 316 336 0 336 335 0 317 337 0 337 336 0 318 338 0 338 337 0
		 319 339 0 339 338 0 320 339 0 321 341 0 341 340 0 340 320 0 322 342 0;
	setAttr ".ed[664:779]" 342 341 0 323 343 0 343 342 0 324 344 0 344 343 0 325 345 0
		 345 344 0 326 346 0 346 345 0 327 347 0 347 346 0 328 348 0 348 347 0 329 349 0 349 348 0
		 330 350 0 350 349 0 331 351 0 351 350 0 332 352 0 352 351 0 333 353 0 353 352 0 334 354 0
		 354 353 0 335 355 0 355 354 0 336 356 0 356 355 0 337 357 0 357 356 0 338 358 0 358 357 0
		 339 359 0 359 358 0 340 359 0 341 361 0 361 360 0 360 340 0 342 362 0 362 361 0 343 363 0
		 363 362 0 344 364 0 364 363 0 345 365 0 365 364 0 346 366 0 366 365 0 347 367 0 367 366 0
		 348 368 0 368 367 0 349 369 0 369 368 0 350 370 0 370 369 0 351 371 0 371 370 0 352 372 0
		 372 371 0 353 373 0 373 372 0 354 374 0 374 373 0 355 375 0 375 374 0 356 376 0 376 375 0
		 357 377 0 377 376 0 358 378 0 378 377 0 359 379 0 379 378 0 360 379 0 0 380 0 380 1 0
		 380 2 0 380 3 0 380 4 0 380 5 0 380 6 0 380 7 0 380 8 0 380 9 0 380 10 0 380 11 0
		 380 12 0 380 13 0 380 14 0 380 15 0 380 16 0 380 17 0 380 18 0 380 19 0 361 381 0
		 381 360 0 362 381 0 363 381 0 364 381 0 365 381 0 366 381 0 367 381 0 368 381 0 369 381 0
		 370 381 0 371 381 0 372 381 0 373 381 0 374 381 0 375 381 0 376 381 0 377 381 0 378 381 0
		 379 381 0;
	setAttr -s 1560 ".n";
	setAttr ".n[0:165]" -type "float3"  1e+020 1e+020 1e+020 1e+020 1e+020 1e+020
		 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 -0.123121 -0.92631602 -0.35606 -0.162241
		 -0.90253597 -0.398882 -0.069080003 -0.86645198 -0.49445799 -0.0039499998 -0.90604401
		 -0.42316401 -0.162241 -0.90253597 -0.398882 -0.213486 -0.87903398 -0.42629001 -0.154397
		 -0.82732397 -0.54009002 -0.069080003 -0.86645198 -0.49445799 -0.213486 -0.87903398
		 -0.42629001 -0.27184001 -0.85811001 -0.43560299 -0.25154901 -0.79248899 -0.55559403
		 -0.154397 -0.82732397 -0.54009002 -0.27184001 -0.85811001 -0.43560299 -0.33159 -0.84181398
		 -0.425908 -0.351026 -0.76535797 -0.53945202 -0.25154901 -0.79248899 -0.55559403 -0.33159
		 -0.84181398 -0.425908 -0.386888 -0.83174002 -0.39815301 -0.44308999 -0.748586 -0.49324399
		 -0.351026 -0.76535797 -0.53945202 -0.386888 -0.83174002 -0.39815301 -0.43232 -0.82887501
		 -0.355057 -0.518731 -0.74381602 -0.42149401 -0.44308999 -0.748586 -0.49324399 -0.43232
		 -0.82887501 -0.355057 -0.46344 -0.83349901 -0.30083701 -0.57054198 -0.751513 -0.33122399
		 -0.518731 -0.74381602 -0.42149401 -0.46344 -0.83349901 -0.30083701 -0.477202 -0.84515899
		 -0.24080101 -0.593454 -0.770926 -0.231271 -0.57054198 -0.751513 -0.33122399 -0.477202
		 -0.84515899 -0.24080101 -0.472258 -0.86271399 -0.18082599 -0.58522201 -0.80015302
		 -0.13142 -0.593454 -0.770926 -0.231271 -0.472258 -0.86271399 -0.18082599 -0.449092
		 -0.88444501 -0.126782 -0.54665297 -0.83633298 -0.041444 -0.58522201 -0.80015302 -0.13142
		 -0.449092 -0.88444501 -0.126782 -0.40997201 -0.90822601 -0.083959997 -0.48152301
		 -0.875925 0.029850001 -0.54665297 -0.83633298 -0.041444 -0.40997201 -0.90822601 -0.083959997
		 -0.35872701 -0.93172801 -0.056552 -0.39620599 -0.91505402 0.075483002 -0.48152301
		 -0.875925 0.029850001 -0.35872701 -0.93172801 -0.056552 -0.30037299 -0.95265102 -0.04724
		 -0.299054 -0.949889 0.090985999 -0.39620599 -0.91505402 0.075483002 -0.30037299 -0.95265102
		 -0.04724 -0.240623 -0.96894699 -0.056935001 -0.199577 -0.97702003 0.074844003 -0.299054
		 -0.949889 0.090985999 -0.240623 -0.96894699 -0.056935001 -0.185325 -0.97902101 -0.084688999
		 -0.107513 -0.99379098 0.028636999 -0.199577 -0.97702003 0.074844003 -0.185325 -0.97902101
		 -0.084688999 -0.139893 -0.98188603 -0.127786 -0.031872999 -0.99856198 -0.043113999
		 -0.107513 -0.99379098 0.028636999 -0.139893 -0.98188603 -0.127786 -0.108772 -0.97726297
		 -0.182005 0.019939 -0.99086398 -0.13338301 -0.031872999 -0.99856198 -0.043113999
		 -0.108772 -0.97726297 -0.182005 -0.095011003 -0.96560299 -0.24204101 0.042849999
		 -0.971452 -0.233336 0.019939 -0.99086398 -0.13338301 -0.095011003 -0.96560299 -0.24204101
		 -0.099955 -0.948048 -0.302017 0.034619 -0.94222498 -0.333188 0.042849999 -0.971452
		 -0.233336 0.034619 -0.94222498 -0.333188 -0.0039499998 -0.90604401 -0.42316401 0.12529001
		 -0.86450797 -0.486752 0.179719 -0.91556698 -0.35977501 -0.0039499998 -0.90604401
		 -0.42316401 -0.069080003 -0.86645198 -0.49445799 0.033376999 -0.808635 -0.587363
		 0.12529001 -0.86450797 -0.486752 -0.069080003 -0.86645198 -0.49445799 -0.154397 -0.82732397
		 -0.54009002 -0.087024003 -0.753416 -0.65175998 0.033376999 -0.808635 -0.587363 -0.154397
		 -0.82732397 -0.54009002 -0.25154901 -0.79248899 -0.55559403 -0.22412699 -0.70425701
		 -0.673639 -0.087024003 -0.753416 -0.65175998 -0.25154901 -0.79248899 -0.55559403
		 -0.351026 -0.76535797 -0.53945202 -0.36451 -0.66596901 -0.650859 -0.22412699 -0.70425701
		 -0.673639 -0.351026 -0.76535797 -0.53945202 -0.44308999 -0.748586 -0.49324399 -0.49443299
		 -0.64230001 -0.58565003 -0.36451 -0.66596901 -0.650859 -0.44308999 -0.748586 -0.49324399
		 -0.518731 -0.74381602 -0.42149401 -0.60117799 -0.63556802 -0.484395 -0.49443299 -0.64230001
		 -0.58565003 -0.518731 -0.74381602 -0.42149401 -0.57054198 -0.751513 -0.33122399 -0.67429602
		 -0.64643103 -0.35700399 -0.60117799 -0.63556802 -0.484395 -0.57054198 -0.751513 -0.33122399
		 -0.593454 -0.770926 -0.231271 -0.70662898 -0.67382598 -0.215949 -0.67429602 -0.64643103
		 -0.35700399 -0.593454 -0.770926 -0.231271 -0.58522201 -0.80015302 -0.13142 -0.69501197
		 -0.71507198 -0.075037003 -0.70662898 -0.67382598 -0.215949 -0.58522201 -0.80015302
		 -0.13142 -0.54665297 -0.83633298 -0.041444 -0.64058298 -0.76612997 0.051940002 -0.69501197
		 -0.71507198 -0.075037003 -0.54665297 -0.83633298 -0.041444 -0.48152301 -0.875925
		 0.029850001 -0.54866999 -0.82200402 0.152551 -0.64058298 -0.76612997 0.051940002
		 -0.48152301 -0.875925 0.029850001 -0.39620599 -0.91505402 0.075483002 -0.428269 -0.87722301
		 0.216948 -0.54866999 -0.82200402 0.152551 -0.39620599 -0.91505402 0.075483002 -0.299054
		 -0.949889 0.090985999 -0.29116601 -0.92638201 0.23882701 -0.428269 -0.87722301 0.216948
		 -0.299054 -0.949889 0.090985999 -0.199577 -0.97702003 0.074844003 -0.150783 -0.96467
		 0.216047 -0.29116601 -0.92638201 0.23882701 -0.199577 -0.97702003 0.074844003 -0.107513
		 -0.99379098 0.028636999 -0.02086 -0.98833799 0.150838 -0.150783 -0.96467 0.216047
		 -0.107513 -0.99379098 0.028636999 -0.031872999 -0.99856198 -0.043113999 0.085885003
		 -0.99506998 0.049582999 -0.02086 -0.98833799 0.150838 -0.031872999 -0.99856198 -0.043113999
		 0.019939 -0.99086398 -0.13338301 0.159003 -0.98420697 -0.077808 0.085885003 -0.99506998
		 0.049582999 0.019939 -0.99086398 -0.13338301 0.042849999 -0.971452 -0.233336 0.19133601
		 -0.95681202 -0.218863 0.159003 -0.98420697 -0.077808 0.042849999 -0.971452 -0.233336
		 0.034619 -0.94222498 -0.333188 0.179719 -0.91556698 -0.35977501 0.19133601 -0.95681202
		 -0.218863 0.179719 -0.91556698 -0.35977501 0.12529001 -0.86450797 -0.486752 0.254105
		 -0.80218798 -0.54030102 0.323439 -0.86722898 -0.37855199 0.12529001 -0.86450797 -0.486752
		 0.033376999 -0.808635 -0.587363;
	setAttr ".n[166:331]" -type "float3"  0.137022 -0.73101401 -0.66846299 0.254105
		 -0.80218798 -0.54030102 0.033376999 -0.808635 -0.587363 -0.087024003 -0.753416 -0.65175998
		 -0.016349999 -0.66067398 -0.75049502 0.137022 -0.73101401 -0.66846299 -0.087024003
		 -0.753416 -0.65175998 -0.22412699 -0.70425701 -0.673639 -0.190997 -0.59805202 -0.77836603
		 -0.016349999 -0.66067398 -0.75049502 -0.22412699 -0.70425701 -0.673639 -0.36451 -0.66596901
		 -0.650859 -0.36982399 -0.54927897 -0.74934798 -0.190997 -0.59805202 -0.77836603 -0.36451
		 -0.66596901 -0.650859 -0.49443299 -0.64230001 -0.58565003 -0.53532499 -0.51912999
		 -0.666282 -0.36982399 -0.54927897 -0.74934798 -0.49443299 -0.64230001 -0.58565003
		 -0.60117799 -0.63556802 -0.484395 -0.67130101 -0.51055402 -0.53729802 -0.53532499
		 -0.51912999 -0.666282 -0.60117799 -0.63556802 -0.484395 -0.67429602 -0.64643103 -0.35700399
		 -0.76444203 -0.52439201 -0.37502301 -0.67130101 -0.51055402 -0.53729802 -0.67429602
		 -0.64643103 -0.35700399 -0.70662898 -0.67382598 -0.215949 -0.80562901 -0.55928898
		 -0.19533999 -0.76444203 -0.52439201 -0.37502301 -0.70662898 -0.67382598 -0.215949
		 -0.69501197 -0.71507198 -0.075037003 -0.79083103 -0.61182898 -0.01584 -0.80562901
		 -0.55928898 -0.19533999 -0.69501197 -0.71507198 -0.075037003 -0.64058298 -0.76612997
		 0.051940002 -0.721497 -0.67686999 0.145908 -0.79083103 -0.61182898 -0.01584 -0.64058298
		 -0.76612997 0.051940002 -0.54866999 -0.82200402 0.152551 -0.60441399 -0.748043 0.27407101
		 -0.721497 -0.67686999 0.145908 -0.54866999 -0.82200402 0.152551 -0.428269 -0.87722301
		 0.216948 -0.451042 -0.81838399 0.35610199 -0.60441399 -0.748043 0.27407101 -0.428269
		 -0.87722301 0.216948 -0.29116601 -0.92638201 0.23882701 -0.27639499 -0.88100499 0.383973
		 -0.451042 -0.81838399 0.35610199 -0.29116601 -0.92638201 0.23882701 -0.150783 -0.96467
		 0.216047 -0.097567998 -0.92977798 0.35495499 -0.27639499 -0.88100499 0.383973 -0.150783
		 -0.96467 0.216047 -0.02086 -0.98833799 0.150838 0.067933001 -0.95992798 0.271889
		 -0.097567998 -0.92977798 0.35495499 -0.02086 -0.98833799 0.150838 0.085885003 -0.99506998
		 0.049582999 0.20390899 -0.96850401 0.142905 0.067933001 -0.95992798 0.271889 0.085885003
		 -0.99506998 0.049582999 0.159003 -0.98420697 -0.077808 0.29705 -0.95466602 -0.019370001
		 0.20390899 -0.96850401 0.142905 0.159003 -0.98420697 -0.077808 0.19133601 -0.95681202
		 -0.218863 0.33823699 -0.91976899 -0.19905201 0.29705 -0.95466602 -0.019370001 0.19133601
		 -0.95681202 -0.218863 0.179719 -0.91556698 -0.35977501 0.323439 -0.86722898 -0.37855199
		 0.33823699 -0.91976899 -0.19905201 0.323439 -0.86722898 -0.37855199 0.254105 -0.80218798
		 -0.54030102 0.377823 -0.72051001 -0.58147699 0.460531 -0.79809499 -0.38852999 0.254105
		 -0.80218798 -0.54030102 0.137022 -0.73101401 -0.66846299 0.238157 -0.63560802 -0.73435998
		 0.377823 -0.72051001 -0.58147699 0.137022 -0.73101401 -0.66846299 -0.016349999 -0.66067398
		 -0.75049502 0.055202 -0.5517 -0.832214 0.238157 -0.63560802 -0.73435998 -0.016349999
		 -0.66067398 -0.75049502 -0.190997 -0.59805202 -0.77836603 -0.15313099 -0.477 -0.86546099
		 0.055202 -0.5517 -0.832214 -0.190997 -0.59805202 -0.77836603 -0.36982399 -0.54927897
		 -0.74934798 -0.36645001 -0.41881901 -0.83084601 -0.15313099 -0.477 -0.86546099 -0.36982399
		 -0.54927897 -0.74934798 -0.53532499 -0.51912999 -0.666282 -0.56387401 -0.38285401
		 -0.73175699 -0.36645001 -0.41881901 -0.83084601 -0.53532499 -0.51912999 -0.666282
		 -0.67130101 -0.51055402 -0.53729802 -0.72607702 -0.37262499 -0.57789499 -0.56387401
		 -0.38285401 -0.73175699 -0.67130101 -0.51055402 -0.53729802 -0.76444203 -0.52439201
		 -0.37502301 -0.837183 -0.38913199 -0.38431999 -0.72607702 -0.37262499 -0.57789499
		 -0.76444203 -0.52439201 -0.37502301 -0.80562901 -0.55928898 -0.19533999 -0.88631397
		 -0.43076 -0.16998 -0.837183 -0.38913199 -0.38431999 -0.80562901 -0.55928898 -0.19533999
		 -0.79083103 -0.61182898 -0.01584 -0.868662 -0.49343401 0.044142999 -0.88631397 -0.43076
		 -0.16998 -0.79083103 -0.61182898 -0.01584 -0.721497 -0.67686999 0.145908 -0.78595501
		 -0.57101899 0.23708899 -0.868662 -0.49343401 0.044142999 -0.721497 -0.67686999 0.145908
		 -0.60441399 -0.748043 0.27407101 -0.64628899 -0.65592098 0.389972 -0.78595501 -0.57101899
		 0.23708899 -0.60441399 -0.748043 0.27407101 -0.451042 -0.81838399 0.35610199 -0.46333399
		 -0.739829 0.48782599 -0.64628899 -0.65592098 0.389972 -0.451042 -0.81838399 0.35610199
		 -0.27639499 -0.88100499 0.383973 -0.25500101 -0.814529 0.52107298 -0.46333399 -0.739829
		 0.48782599 -0.27639499 -0.88100499 0.383973 -0.097567998 -0.92977798 0.35495499 -0.041682001
		 -0.87270898 0.486458 -0.25500101 -0.814529 0.52107298 -0.097567998 -0.92977798 0.35495499
		 0.067933001 -0.95992798 0.271889 0.155742 -0.908674 0.38736901 -0.041682001 -0.87270898
		 0.486458 0.067933001 -0.95992798 0.271889 0.20390899 -0.96850401 0.142905 0.31794599
		 -0.91890401 0.23350701 0.155742 -0.908674 0.38736901 0.20390899 -0.96850401 0.142905
		 0.29705 -0.95466602 -0.019370001 0.42905101 -0.90239698 0.039932001 0.31794599 -0.91890401
		 0.23350701 0.29705 -0.95466602 -0.019370001 0.33823699 -0.91976899 -0.19905201 0.47818199
		 -0.86076897 -0.17440701 0.42905101 -0.90239698 0.039932001 0.33823699 -0.91976899
		 -0.19905201 0.323439 -0.86722898 -0.37855199 0.460531 -0.79809499 -0.38852999 0.47818199
		 -0.86076897 -0.17440701 0.460531 -0.79809499 -0.38852999 0.377823 -0.72051001 -0.58147699
		 0.49293 -0.62145001 -0.60895002 0.58708501 -0.709773 -0.38929901 0.377823 -0.72051001
		 -0.58147699 0.238157 -0.63560802 -0.73435998 0.33393401 -0.52479702 -0.78299201 0.49293
		 -0.62145001 -0.60895002 0.238157 -0.63560802 -0.73435998 0.055202 -0.5517 -0.832214
		 0.12565801 -0.42927599 -0.89438897 0.33393401 -0.52479702 -0.78299201;
	setAttr ".n[332:497]" -type "float3"  0.055202 -0.5517 -0.832214 -0.15313099
		 -0.477 -0.86546099 -0.111509 -0.34423801 -0.93223703 0.12565801 -0.42927599 -0.89438897
		 -0.15313099 -0.477 -0.86546099 -0.36645001 -0.41881901 -0.83084601 -0.354352 -0.278005
		 -0.89283103 -0.111509 -0.34423801 -0.93223703 -0.36645001 -0.41881901 -0.83084601
		 -0.56387401 -0.38285401 -0.73175699 -0.57910001 -0.23706201 -0.780029 -0.354352 -0.278005
		 -0.89283103 -0.56387401 -0.38285401 -0.73175699 -0.72607702 -0.37262499 -0.57789499
		 -0.76375198 -0.225417 -0.60487199 -0.57910001 -0.23706201 -0.780029 -0.72607702 -0.37262499
		 -0.57789499 -0.837183 -0.38913199 -0.38431999 -0.89023501 -0.24420901 -0.384505 -0.76375198
		 -0.225417 -0.60487199 -0.837183 -0.38913199 -0.38431999 -0.88631397 -0.43076 -0.16998
		 -0.94616598 -0.29159799 -0.14050101 -0.89023501 -0.24420901 -0.384505 -0.88631397
		 -0.43076 -0.16998 -0.868662 -0.49343401 0.044142999 -0.92607099 -0.36294699 0.103257
		 -0.94616598 -0.29159799 -0.14050101 -0.868662 -0.49343401 0.044142999 -0.78595501
		 -0.57101899 0.23708899 -0.83191699 -0.45127001 0.322907 -0.92607099 -0.36294699 0.103257
		 -0.78595501 -0.57101899 0.23708899 -0.64628899 -0.65592098 0.389972 -0.67291999 -0.54792303
		 0.49695 -0.83191699 -0.45127001 0.322907 -0.64628899 -0.65592098 0.389972 -0.46333399
		 -0.739829 0.48782599 -0.464645 -0.64344299 0.608347 -0.67291999 -0.54792303 0.49695
		 -0.46333399 -0.739829 0.48782599 -0.25500101 -0.814529 0.52107298 -0.227478 -0.72848201
		 0.64619499 -0.464645 -0.64344299 0.608347 -0.25500101 -0.814529 0.52107298 -0.041682001
		 -0.87270898 0.486458 0.015365 -0.79471397 0.60678899 -0.227478 -0.72848201 0.64619499
		 -0.041682001 -0.87270898 0.486458 0.155742 -0.908674 0.38736901 0.24011301 -0.835657
		 0.49398699 0.015365 -0.79471397 0.60678899 0.155742 -0.908674 0.38736901 0.31794599
		 -0.91890401 0.23350701 0.424766 -0.84730297 0.318829 0.24011301 -0.835657 0.49398699
		 0.31794599 -0.91890401 0.23350701 0.42905101 -0.90239698 0.039932001 0.55124801 -0.828511
		 0.098462999 0.424766 -0.84730297 0.318829 0.42905101 -0.90239698 0.039932001 0.47818199
		 -0.86076897 -0.17440701 0.60717899 -0.78112203 -0.145541 0.55124801 -0.828511 0.098462999
		 0.47818199 -0.86076897 -0.17440701 0.460531 -0.79809499 -0.38852999 0.58708501 -0.709773
		 -0.38929901 0.60717899 -0.78112203 -0.145541 0.58708501 -0.709773 -0.38929901 0.49293
		 -0.62145001 -0.60895002 0.596434 -0.50741798 -0.62192702 0.69980401 -0.60438699 -0.38077599
		 0.49293 -0.62145001 -0.60895002 0.33393401 -0.52479702 -0.78299201 0.421875 -0.40130499
		 -0.81300402 0.596434 -0.50741798 -0.62192702 0.33393401 -0.52479702 -0.78299201 0.12565801
		 -0.42927599 -0.89438897 0.193214 -0.296435 -0.935305 0.421875 -0.40130499 -0.81300402
		 0.12565801 -0.42927599 -0.89438897 -0.111509 -0.34423801 -0.93223703 -0.067166999
		 -0.20307299 -0.97685701 0.193214 -0.296435 -0.935305 -0.111509 -0.34423801 -0.93223703
		 -0.354352 -0.278005 -0.89283103 -0.33377901 -0.130358 -0.93359399 -0.067166999 -0.20307299
		 -0.97685701 -0.354352 -0.278005 -0.89283103 -0.57910001 -0.23706201 -0.780029 -0.58052498
		 -0.085408002 -0.80975097 -0.33377901 -0.130358 -0.93359399 -0.57910001 -0.23706201
		 -0.780029 -0.76375198 -0.225417 -0.60487199 -0.78325099 -0.072622001 -0.61744899
		 -0.58052498 -0.085408002 -0.80975097 -0.76375198 -0.225417 -0.60487199 -0.89023501
		 -0.24420901 -0.384505 -0.922113 -0.093253002 -0.375514 -0.78325099 -0.072622001 -0.61744899
		 -0.89023501 -0.24420901 -0.384505 -0.94616598 -0.29159799 -0.14050101 -0.98351902
		 -0.145281 -0.107627 -0.922113 -0.093253002 -0.375514 -0.94616598 -0.29159799 -0.14050101
		 -0.92607099 -0.36294699 0.103257 -0.96145701 -0.22361299 0.15999 -0.98351902 -0.145281
		 -0.107627 -0.92607099 -0.36294699 0.103257 -0.83191699 -0.45127001 0.322907 -0.85808802
		 -0.320582 0.40113899 -0.96145701 -0.22361299 0.15999 -0.83191699 -0.45127001 0.322907
		 -0.67291999 -0.54792303 0.49695 -0.68352902 -0.42669401 0.59221601 -0.85808802 -0.320582
		 0.40113899 -0.67291999 -0.54792303 0.49695 -0.464645 -0.64344299 0.608347 -0.45486701
		 -0.53156501 0.714517 -0.68352902 -0.42669401 0.59221601 -0.464645 -0.64344299 0.608347
		 -0.227478 -0.72848201 0.64619499 -0.19448701 -0.62492698 0.75607002 -0.45486701 -0.53156501
		 0.714517 -0.227478 -0.72848201 0.64619499 0.015365 -0.79471397 0.60678899 0.072125003
		 -0.69764203 0.712807 -0.19448701 -0.62492698 0.75607002 0.015365 -0.79471397 0.60678899
		 0.24011301 -0.835657 0.49398699 0.31887099 -0.74259198 0.58896399 0.072125003 -0.69764203
		 0.712807 0.24011301 -0.835657 0.49398699 0.424766 -0.84730297 0.318829 0.52159798
		 -0.75537699 0.396662 0.31887099 -0.74259198 0.58896399 0.424766 -0.84730297 0.318829
		 0.55124801 -0.828511 0.098462999 0.66046 -0.73474699 0.154727 0.52159798 -0.75537699
		 0.396662 0.55124801 -0.828511 0.098462999 0.60717899 -0.78112203 -0.145541 0.72186601
		 -0.68271899 -0.11316 0.66046 -0.73474699 0.154727 0.60717899 -0.78112203 -0.145541
		 0.58708501 -0.709773 -0.38929901 0.69980401 -0.60438699 -0.38077599 0.72186601 -0.68271899
		 -0.11316 0.69980401 -0.60438699 -0.38077599 0.596434 -0.50741798 -0.62192702 0.68574601
		 -0.38117999 -0.62004298 0.79586703 -0.48448101 -0.36314499 0.596434 -0.50741798 -0.62192702
		 0.421875 -0.40130499 -0.81300402 0.49978799 -0.26813799 -0.82359803 0.68574601 -0.38117999
		 -0.62004298 0.421875 -0.40130499 -0.81300402 0.193214 -0.296435 -0.935305 0.25619501
		 -0.15641899 -0.95388502 0.49978799 -0.26813799 -0.82359803 0.193214 -0.296435 -0.935305
		 -0.067166999 -0.20307299 -0.97685701 -0.021190001 -0.056960002 -0.99815202 0.25619501
		 -0.15641899 -0.95388502 -0.067166999 -0.20307299 -0.97685701 -0.33377901 -0.130358
		 -0.93359399;
	setAttr ".n[498:663]" -type "float3"  -0.30521199 0.020502999 -0.95206302 -0.021190001
		 -0.056960002 -0.99815202 -0.33377901 -0.130358 -0.93359399 -0.58052498 -0.085408002
		 -0.80975097 -0.56807202 0.068388999 -0.82013297 -0.30521199 0.020502999 -0.95206302
		 -0.58052498 -0.085408002 -0.80975097 -0.78325099 -0.072622001 -0.61744899 -0.78403598
		 0.082009003 -0.615273 -0.56807202 0.068388999 -0.82013297 -0.78325099 -0.072622001
		 -0.61744899 -0.922113 -0.093253002 -0.375514 -0.93196702 0.060031001 -0.357539 -0.78403598
		 0.082009003 -0.615273 -0.922113 -0.093253002 -0.375514 -0.98351902 -0.145281 -0.107627
		 -0.997383 0.0046049999 -0.072158001 -0.93196702 0.060031001 -0.357539 -0.98351902
		 -0.145281 -0.107627 -0.96145701 -0.22361299 0.15999 -0.97387999 -0.078841999 0.212935
		 -0.997383 0.0046049999 -0.072158001 -0.96145701 -0.22361299 0.15999 -0.85808802 -0.320582
		 0.40113899 -0.86375999 -0.182142 0.469832 -0.97387999 -0.078841999 0.212935 -0.85808802
		 -0.320582 0.40113899 -0.68352902 -0.42669401 0.59221601 -0.67780203 -0.295185 0.67338699
		 -0.86375999 -0.182142 0.469832 -0.68352902 -0.42669401 0.59221601 -0.45486701 -0.53156501
		 0.714517 -0.43420801 -0.406903 0.803675 -0.67780203 -0.295185 0.67338699 -0.45486701
		 -0.53156501 0.714517 -0.19448701 -0.62492698 0.75607002 -0.15682399 -0.50636202 0.84794098
		 -0.43420801 -0.406903 0.803675 -0.19448701 -0.62492698 0.75607002 0.072125003 -0.69764203
		 0.712807 0.12719899 -0.58382601 0.801853 -0.15682399 -0.50636202 0.84794098 0.072125003
		 -0.69764203 0.712807 0.31887099 -0.74259198 0.58896399 0.39005801 -0.63171101 0.66992199
		 0.12719899 -0.58382601 0.801853 0.31887099 -0.74259198 0.58896399 0.52159798 -0.75537699
		 0.396662 0.60602301 -0.64533198 0.46506301 0.39005801 -0.63171101 0.66992199 0.52159798
		 -0.75537699 0.396662 0.66046 -0.73474699 0.154727 0.75395298 -0.62335402 0.20732801
		 0.60602301 -0.64533198 0.46506301 0.66046 -0.73474699 0.154727 0.72186601 -0.68271899
		 -0.11316 0.81936902 -0.56792802 -0.078051999 0.75395298 -0.62335402 0.20732801 0.72186601
		 -0.68271899 -0.11316 0.69980401 -0.60438699 -0.38077599 0.79586703 -0.48448101 -0.36314499
		 0.81936902 -0.56792802 -0.078051999 0.79586703 -0.48448101 -0.36314499 0.68574601
		 -0.38117999 -0.62004298 0.75867701 -0.245784 -0.60332298 0.87291503 -0.35294801 -0.33681899
		 0.68574601 -0.38117999 -0.62004298 0.49978799 -0.26813799 -0.82359803 0.56576598
		 -0.12851501 -0.81448901 0.75867701 -0.245784 -0.60332298 0.49978799 -0.26813799 -0.82359803
		 0.25619501 -0.15641899 -0.95388502 0.31306401 -0.012619 -0.94964802 0.56576598 -0.12851501
		 -0.81448901 0.25619501 -0.15641899 -0.95388502 -0.021190001 -0.056960002 -0.99815202
		 0.025308 0.090558 -0.99557 0.31306401 -0.012619 -0.94964802 -0.021190001 -0.056960002
		 -0.99815202 -0.30521199 0.020502999 -0.95206302 -0.269335 0.170919 -0.94775802 0.025308
		 0.090558 -0.99557 -0.30521199 0.020502999 -0.95206302 -0.56807202 0.068388999 -0.82013297
		 -0.542023 0.220595 -0.81089401 -0.269335 0.170919 -0.94775802 -0.56807202 0.068388999
		 -0.82013297 -0.78403598 0.082009003 -0.615273 -0.76606202 0.234725 -0.59837502 -0.542023
		 0.220595 -0.81089401 -0.78403598 0.082009003 -0.615273 -0.93196702 0.060031001 -0.357539
		 -0.91952401 0.211925 -0.33100399 -0.76606202 0.234725 -0.59837502 -0.93196702 0.060031001
		 -0.357539 -0.997383 0.0046049999 -0.072158001 -0.98738599 0.15442701 -0.034952 -0.91952401
		 0.211925 -0.33100399 -0.997383 0.0046049999 -0.072158001 -0.97387999 -0.078841999
		 0.212935 -0.96300501 0.067859001 0.26080099 -0.98738599 0.15442701 -0.034952 -0.97387999
		 -0.078841999 0.212935 -0.86375999 -0.182142 0.469832 -0.84876698 -0.039303999 0.52730399
		 -0.96300501 0.067859001 0.26080099 -0.86375999 -0.182142 0.469832 -0.67780203 -0.295185
		 0.67338699 -0.65585601 -0.156573 0.73847002 -0.84876698 -0.039303999 0.52730399 -0.67780203
		 -0.295185 0.67338699 -0.43420801 -0.406903 0.803675 -0.40315399 -0.27246901 0.87362897
		 -0.65585601 -0.156573 0.73847002 -0.43420801 -0.406903 0.803675 -0.15682399 -0.50636202
		 0.84794098 -0.115398 -0.37564701 0.91955 -0.40315399 -0.27246901 0.87362897 -0.15682399
		 -0.50636202 0.84794098 0.12719899 -0.58382601 0.801853 0.179245 -0.456007 0.87173897
		 -0.115398 -0.37564701 0.91955 0.12719899 -0.58382601 0.801853 0.39005801 -0.63171101
		 0.66992199 0.45193201 -0.505683 0.73487502 0.179245 -0.456007 0.87173897 0.39005801
		 -0.63171101 0.66992199 0.60602301 -0.64533198 0.46506301 0.67597198 -0.519813 0.52235597
		 0.45193201 -0.505683 0.73487502 0.60602301 -0.64533198 0.46506301 0.75395298 -0.62335402
		 0.20732801 0.82943398 -0.497013 0.25498399 0.67597198 -0.519813 0.52235597 0.75395298
		 -0.62335402 0.20732801 0.81936902 -0.56792802 -0.078051999 0.89729601 -0.43951499
		 -0.041067 0.82943398 -0.497013 0.25498399 0.81936902 -0.56792802 -0.078051999 0.79586703
		 -0.48448101 -0.36314499 0.87291503 -0.35294801 -0.33681899 0.89729601 -0.43951499
		 -0.041067 0.87291503 -0.35294801 -0.33681899 0.75867701 -0.245784 -0.60332298 0.81345803
		 -0.104491 -0.57216102 0.929079 -0.212952 -0.30242899 0.75867701 -0.245784 -0.60332298
		 0.56576598 -0.12851501 -0.81448901 0.618209 0.014199 -0.78588498 0.81345803 -0.104491
		 -0.57216102 0.56576598 -0.12851501 -0.81448901 0.31306401 -0.012619 -0.94964802 0.36244601
		 0.13149901 -0.92268097 0.618209 0.014199 -0.78588498 0.31306401 -0.012619 -0.94964802
		 0.025308 0.090558 -0.99557 0.071204998 0.235926 -0.96915901 0.36244601 0.13149901
		 -0.92268097 0.025308 0.090558 -0.99557 -0.269335 0.170919 -0.94775802 -0.227007 0.31726
		 -0.92076802 0.071204998 0.235926 -0.96915901 -0.269335 0.170919 -0.94775802 -0.542023
		 0.220595 -0.81089401 -0.50299698 0.36753801 -0.78224701 -0.227007 0.31726 -0.92076802;
	setAttr ".n[664:829]" -type "float3"  -0.542023 0.220595 -0.81089401 -0.76606202
		 0.234725 -0.59837502 -0.72975099 0.38183799 -0.56715298 -0.50299698 0.36753801 -0.78224701
		 -0.76606202 0.234725 -0.59837502 -0.91952401 0.211925 -0.33100399 -0.88507199 0.358762
		 -0.296543 -0.72975099 0.38183799 -0.56715298 -0.91952401 0.211925 -0.33100399 -0.98738599
		 0.15442701 -0.034952 -0.95375502 0.30056801 0.0030950001 -0.88507199 0.358762 -0.296543
		 -0.98738599 0.15442701 -0.034952 -0.96300501 0.067859001 0.26080099 -0.929079 0.212952
		 0.30243 -0.95375502 0.30056801 0.0030950001 -0.96300501 0.067859001 0.26080099 -0.84876698
		 -0.039303999 0.52730399 -0.81345803 0.10449 0.57216102 -0.929079 0.212952 0.30243
		 -0.84876698 -0.039303999 0.52730399 -0.65585601 -0.156573 0.73847002 -0.618209 -0.014199
		 0.78588498 -0.81345803 0.10449 0.57216102 -0.65585601 -0.156573 0.73847002 -0.40315399
		 -0.27246901 0.87362897 -0.36244699 -0.13149901 0.92268097 -0.618209 -0.014199 0.78588498
		 -0.40315399 -0.27246901 0.87362897 -0.115398 -0.37564701 0.91955 -0.071204998 -0.235926
		 0.96915901 -0.36244699 -0.13149901 0.92268097 -0.115398 -0.37564701 0.91955 0.179245
		 -0.456007 0.87173897 0.227006 -0.31726 0.92076802 -0.071204998 -0.235926 0.96915901
		 0.179245 -0.456007 0.87173897 0.45193201 -0.505683 0.73487502 0.50299698 -0.36753801
		 0.78224701 0.227006 -0.31726 0.92076802 0.45193201 -0.505683 0.73487502 0.67597198
		 -0.519813 0.52235597 0.72975099 -0.38183901 0.56715298 0.50299698 -0.36753801 0.78224701
		 0.67597198 -0.519813 0.52235597 0.82943398 -0.497013 0.25498399 0.88507199 -0.358762
		 0.296543 0.72975099 -0.38183901 0.56715298 0.82943398 -0.497013 0.25498399 0.89729601
		 -0.43951499 -0.041067 0.95375502 -0.30056801 -0.003094 0.88507199 -0.358762 0.296543
		 0.89729601 -0.43951499 -0.041067 0.87291503 -0.35294801 -0.33681899 0.929079 -0.212952
		 -0.30242899 0.95375502 -0.30056801 -0.003094 0.929079 -0.212952 -0.30242899 0.81345803
		 -0.104491 -0.57216102 0.84876698 0.039303999 -0.52730399 0.96300501 -0.067859001
		 -0.2608 0.81345803 -0.104491 -0.57216102 0.618209 0.014199 -0.78588498 0.65585601
		 0.156573 -0.73847002 0.84876698 0.039303999 -0.52730399 0.618209 0.014199 -0.78588498
		 0.36244601 0.13149901 -0.92268097 0.40315399 0.27246901 -0.87362897 0.65585601 0.156573
		 -0.73847002 0.36244601 0.13149901 -0.92268097 0.071204998 0.235926 -0.96915901 0.115398
		 0.37564701 -0.91955 0.40315399 0.27246901 -0.87362897 0.071204998 0.235926 -0.96915901
		 -0.227007 0.31726 -0.92076802 -0.179245 0.456007 -0.87173897 0.115398 0.37564701
		 -0.91955 -0.227007 0.31726 -0.92076802 -0.50299698 0.36753801 -0.78224701 -0.451933
		 0.505683 -0.73487502 -0.179245 0.456007 -0.87173897 -0.50299698 0.36753801 -0.78224701
		 -0.72975099 0.38183799 -0.56715298 -0.675973 0.519813 -0.52235597 -0.451933 0.505683
		 -0.73487502 -0.72975099 0.38183799 -0.56715298 -0.88507199 0.358762 -0.296543 -0.82943398
		 0.497013 -0.25498399 -0.675973 0.519813 -0.52235597 -0.88507199 0.358762 -0.296543
		 -0.95375502 0.30056801 0.0030950001 -0.89729601 0.43951499 0.041067999 -0.82943398
		 0.497013 -0.25498399 -0.95375502 0.30056801 0.0030950001 -0.929079 0.212952 0.30243
		 -0.87291503 0.352947 0.33682001 -0.89729601 0.43951499 0.041067999 -0.929079 0.212952
		 0.30243 -0.81345803 0.10449 0.57216102 -0.75867701 0.245784 0.60332298 -0.87291503
		 0.352947 0.33682001 -0.81345803 0.10449 0.57216102 -0.618209 -0.014199 0.78588498
		 -0.56576598 0.12851501 0.81448901 -0.75867701 0.245784 0.60332298 -0.618209 -0.014199
		 0.78588498 -0.36244699 -0.13149901 0.92268097 -0.31306401 0.012619 0.94964802 -0.56576598
		 0.12851501 0.81448901 -0.36244699 -0.13149901 0.92268097 -0.071204998 -0.235926 0.96915901
		 -0.025308 -0.090558 0.99557 -0.31306401 0.012619 0.94964802 -0.071204998 -0.235926
		 0.96915901 0.227006 -0.31726 0.92076802 0.269335 -0.170919 0.94775802 -0.025308 -0.090558
		 0.99557 0.227006 -0.31726 0.92076802 0.50299698 -0.36753801 0.78224701 0.54202199
		 -0.220595 0.81089401 0.269335 -0.170919 0.94775802 0.50299698 -0.36753801 0.78224701
		 0.72975099 -0.38183901 0.56715298 0.76606202 -0.234724 0.59837502 0.54202199 -0.220595
		 0.81089401 0.72975099 -0.38183901 0.56715298 0.88507199 -0.358762 0.296543 0.91952401
		 -0.211924 0.33100399 0.76606202 -0.234724 0.59837502 0.88507199 -0.358762 0.296543
		 0.95375502 -0.30056801 -0.003094 0.98738599 -0.15442701 0.034952998 0.91952401 -0.211924
		 0.33100399 0.95375502 -0.30056801 -0.003094 0.929079 -0.212952 -0.30242899 0.96300501
		 -0.067859001 -0.2608 0.98738599 -0.15442701 0.034952998 0.96300501 -0.067859001 -0.2608
		 0.84876698 0.039303999 -0.52730399 0.86375999 0.182142 -0.469832 0.97387999 0.078841001
		 -0.212934 0.84876698 0.039303999 -0.52730399 0.65585601 0.156573 -0.73847002 0.67780203
		 0.295185 -0.67338699 0.86375999 0.182142 -0.469832 0.65585601 0.156573 -0.73847002
		 0.40315399 0.27246901 -0.87362897 0.43420801 0.406903 -0.803675 0.67780203 0.295185
		 -0.67338699 0.40315399 0.27246901 -0.87362897 0.115398 0.37564701 -0.91955 0.15682399
		 0.50636202 -0.84794098 0.43420801 0.406903 -0.803675 0.115398 0.37564701 -0.91955
		 -0.179245 0.456007 -0.87173897 -0.12719899 0.58382601 -0.801853 0.15682399 0.50636202
		 -0.84794098 -0.179245 0.456007 -0.87173897 -0.451933 0.505683 -0.73487502 -0.39005801
		 0.63171202 -0.66992199 -0.12719899 0.58382601 -0.801853 -0.451933 0.505683 -0.73487502
		 -0.675973 0.519813 -0.52235597 -0.60602301 0.64533198 -0.46506301 -0.39005801 0.63171202
		 -0.66992199 -0.675973 0.519813 -0.52235597 -0.82943398 0.497013 -0.25498399;
	setAttr ".n[830:995]" -type "float3"  -0.75395298 0.62335402 -0.20732801 -0.60602301
		 0.64533198 -0.46506301 -0.82943398 0.497013 -0.25498399 -0.89729601 0.43951499 0.041067999
		 -0.81936902 0.56792802 0.078052998 -0.75395298 0.62335402 -0.20732801 -0.89729601
		 0.43951499 0.041067999 -0.87291503 0.352947 0.33682001 -0.79586601 0.48448101 0.36314601
		 -0.81936902 0.56792802 0.078052998 -0.87291503 0.352947 0.33682001 -0.75867701 0.245784
		 0.60332298 -0.68574703 0.38117999 0.62004298 -0.79586601 0.48448101 0.36314601 -0.75867701
		 0.245784 0.60332298 -0.56576598 0.12851501 0.81448901 -0.49978799 0.26813799 0.82359803
		 -0.68574703 0.38117999 0.62004298 -0.56576598 0.12851501 0.81448901 -0.31306401 0.012619
		 0.94964802 -0.25619501 0.15641899 0.95388502 -0.49978799 0.26813799 0.82359803 -0.31306401
		 0.012619 0.94964802 -0.025308 -0.090558 0.99557 0.021190001 0.056960002 0.99815202
		 -0.25619501 0.15641899 0.95388502 -0.025308 -0.090558 0.99557 0.269335 -0.170919
		 0.94775802 0.30521199 -0.020502999 0.95206398 0.021190001 0.056960002 0.99815202
		 0.269335 -0.170919 0.94775802 0.54202199 -0.220595 0.81089401 0.56807101 -0.068388999
		 0.82013297 0.30521199 -0.020502999 0.95206398 0.54202199 -0.220595 0.81089401 0.76606202
		 -0.234724 0.59837502 0.78403598 -0.082009003 0.61527401 0.56807101 -0.068388999 0.82013297
		 0.76606202 -0.234724 0.59837502 0.91952401 -0.211924 0.33100399 0.93196702 -0.060031001
		 0.357539 0.78403598 -0.082009003 0.61527401 0.91952401 -0.211924 0.33100399 0.98738599
		 -0.15442701 0.034952998 0.997383 -0.0046060001 0.072159 0.93196702 -0.060031001 0.357539
		 0.98738599 -0.15442701 0.034952998 0.96300501 -0.067859001 -0.2608 0.97387999 0.078841001
		 -0.212934 0.997383 -0.0046060001 0.072159 0.97387999 0.078841001 -0.212934 0.86375999
		 0.182142 -0.469832 0.85808802 0.320582 -0.40113899 0.96145803 0.22361299 -0.159989
		 0.86375999 0.182142 -0.469832 0.67780203 0.295185 -0.67338699 0.68352902 0.42669401
		 -0.59221703 0.85808802 0.320582 -0.40113899 0.67780203 0.295185 -0.67338699 0.43420801
		 0.406903 -0.803675 0.45486701 0.53156501 -0.714517 0.68352902 0.42669401 -0.59221703
		 0.43420801 0.406903 -0.803675 0.15682399 0.50636202 -0.84794098 0.19448701 0.62492698
		 -0.75607002 0.45486701 0.53156501 -0.714517 0.15682399 0.50636202 -0.84794098 -0.12719899
		 0.58382601 -0.801853 -0.072125003 0.69764203 -0.712807 0.19448701 0.62492698 -0.75607002
		 -0.12719899 0.58382601 -0.801853 -0.39005801 0.63171202 -0.66992199 -0.31887099 0.74259198
		 -0.58896297 -0.072125003 0.69764203 -0.712807 -0.39005801 0.63171202 -0.66992199
		 -0.60602301 0.64533198 -0.46506301 -0.52159798 0.75537801 -0.396662 -0.31887099 0.74259198
		 -0.58896297 -0.60602301 0.64533198 -0.46506301 -0.75395298 0.62335402 -0.20732801
		 -0.66046 0.73474699 -0.154727 -0.52159798 0.75537801 -0.396662 -0.75395298 0.62335402
		 -0.20732801 -0.81936902 0.56792802 0.078052998 -0.72186601 0.68271899 0.113161 -0.66046
		 0.73474699 -0.154727 -0.81936902 0.56792802 0.078052998 -0.79586601 0.48448101 0.36314601
		 -0.69980401 0.60438699 0.380777 -0.72186601 0.68271899 0.113161 -0.79586601 0.48448101
		 0.36314601 -0.68574703 0.38117999 0.62004298 -0.596434 0.50741798 0.62192702 -0.69980401
		 0.60438699 0.380777 -0.68574703 0.38117999 0.62004298 -0.49978799 0.26813799 0.82359803
		 -0.421875 0.40130499 0.81300402 -0.596434 0.50741798 0.62192702 -0.49978799 0.26813799
		 0.82359803 -0.25619501 0.15641899 0.95388502 -0.193214 0.296435 0.935305 -0.421875
		 0.40130499 0.81300402 -0.25619501 0.15641899 0.95388502 0.021190001 0.056960002 0.99815202
		 0.067166999 0.20307299 0.97685701 -0.193214 0.296435 0.935305 0.021190001 0.056960002
		 0.99815202 0.30521199 -0.020502999 0.95206398 0.33377901 0.130358 0.93359399 0.067166999
		 0.20307299 0.97685701 0.30521199 -0.020502999 0.95206398 0.56807101 -0.068388999
		 0.82013297 0.58052498 0.085408002 0.80975097 0.33377901 0.130358 0.93359399 0.56807101
		 -0.068388999 0.82013297 0.78403598 -0.082009003 0.61527401 0.78325099 0.072622001
		 0.61745 0.58052498 0.085408002 0.80975097 0.78403598 -0.082009003 0.61527401 0.93196702
		 -0.060031001 0.357539 0.922113 0.093253002 0.375514 0.78325099 0.072622001 0.61745
		 0.93196702 -0.060031001 0.357539 0.997383 -0.0046060001 0.072159 0.98351902 0.145281
		 0.107627 0.922113 0.093253002 0.375514 0.997383 -0.0046060001 0.072159 0.97387999
		 0.078841001 -0.212934 0.96145803 0.22361299 -0.159989 0.98351902 0.145281 0.107627
		 0.96145803 0.22361299 -0.159989 0.85808802 0.320582 -0.40113899 0.83191699 0.45127001
		 -0.322907 0.92607099 0.362946 -0.103256 0.85808802 0.320582 -0.40113899 0.68352902
		 0.42669401 -0.59221703 0.67291999 0.54792303 -0.49694899 0.83191699 0.45127001 -0.322907
		 0.68352902 0.42669401 -0.59221703 0.45486701 0.53156501 -0.714517 0.464645 0.64344299
		 -0.608347 0.67291999 0.54792303 -0.49694899 0.45486701 0.53156501 -0.714517 0.19448701
		 0.62492698 -0.75607002 0.227478 0.72848201 -0.64619499 0.464645 0.64344299 -0.608347
		 0.19448701 0.62492698 -0.75607002 -0.072125003 0.69764203 -0.712807 -0.015365 0.79471397
		 -0.60678899 0.227478 0.72848201 -0.64619499 -0.072125003 0.69764203 -0.712807 -0.31887099
		 0.74259198 -0.58896297 -0.24011301 0.835657 -0.49398601 -0.015365 0.79471397 -0.60678899
		 -0.31887099 0.74259198 -0.58896297 -0.52159798 0.75537801 -0.396662 -0.424766 0.84730297
		 -0.318829 -0.24011301 0.835657 -0.49398601 -0.52159798 0.75537801 -0.396662 -0.66046
		 0.73474699 -0.154727 -0.55124801 0.828511 -0.098462999 -0.424766 0.84730297 -0.318829
		 -0.66046 0.73474699 -0.154727 -0.72186601 0.68271899 0.113161 -0.60717899 0.78112203
		 0.145541 -0.55124801 0.828511 -0.098462999;
	setAttr ".n[996:1161]" -type "float3"  -0.72186601 0.68271899 0.113161 -0.69980401
		 0.60438699 0.380777 -0.587084 0.709773 0.38929901 -0.60717899 0.78112203 0.145541
		 -0.69980401 0.60438699 0.380777 -0.596434 0.50741798 0.62192702 -0.49293101 0.62145001
		 0.60895002 -0.587084 0.709773 0.38929901 -0.596434 0.50741798 0.62192702 -0.421875
		 0.40130499 0.81300402 -0.33393401 0.52479702 0.78299201 -0.49293101 0.62145001 0.60895002
		 -0.421875 0.40130499 0.81300402 -0.193214 0.296435 0.935305 -0.12565801 0.42927599
		 0.89438897 -0.33393401 0.52479702 0.78299201 -0.193214 0.296435 0.935305 0.067166999
		 0.20307299 0.97685701 0.111509 0.34423801 0.93223703 -0.12565801 0.42927599 0.89438897
		 0.067166999 0.20307299 0.97685701 0.33377901 0.130358 0.93359399 0.354352 0.278005
		 0.89283103 0.111509 0.34423801 0.93223703 0.33377901 0.130358 0.93359399 0.58052498
		 0.085408002 0.80975097 0.57910001 0.23706201 0.780029 0.354352 0.278005 0.89283103
		 0.58052498 0.085408002 0.80975097 0.78325099 0.072622001 0.61745 0.76375198 0.225417
		 0.60487199 0.57910001 0.23706201 0.780029 0.78325099 0.072622001 0.61745 0.922113
		 0.093253002 0.375514 0.89023501 0.24420901 0.384505 0.76375198 0.225417 0.60487199
		 0.922113 0.093253002 0.375514 0.98351902 0.145281 0.107627 0.94616598 0.29159799
		 0.14050201 0.89023501 0.24420901 0.384505 0.98351902 0.145281 0.107627 0.96145803
		 0.22361299 -0.159989 0.92607099 0.362946 -0.103256 0.94616598 0.29159799 0.14050201
		 0.92607099 0.362946 -0.103256 0.83191699 0.45127001 -0.322907 0.78595501 0.57102001
		 -0.23708899 0.86866301 0.49343401 -0.044142 0.83191699 0.45127001 -0.322907 0.67291999
		 0.54792303 -0.49694899 0.64628899 0.655922 -0.389972 0.78595501 0.57102001 -0.23708899
		 0.67291999 0.54792303 -0.49694899 0.464645 0.64344299 -0.608347 0.46333399 0.739829
		 -0.48782599 0.64628899 0.655922 -0.389972 0.464645 0.64344299 -0.608347 0.227478
		 0.72848201 -0.64619499 0.25500101 0.814529 -0.52107298 0.46333399 0.739829 -0.48782599
		 0.227478 0.72848201 -0.64619499 -0.015365 0.79471397 -0.60678899 0.041682001 0.87270898
		 -0.486458 0.25500101 0.814529 -0.52107298 -0.015365 0.79471397 -0.60678899 -0.24011301
		 0.835657 -0.49398601 -0.155742 0.90867501 -0.38736901 0.041682001 0.87270898 -0.486458
		 -0.24011301 0.835657 -0.49398601 -0.424766 0.84730297 -0.318829 -0.31794599 0.91890401
		 -0.23350701 -0.155742 0.90867501 -0.38736901 -0.424766 0.84730297 -0.318829 -0.55124801
		 0.828511 -0.098462999 -0.42905101 0.90239698 -0.039932001 -0.31794599 0.91890401
		 -0.23350701 -0.55124801 0.828511 -0.098462999 -0.60717899 0.78112203 0.145541 -0.47818199
		 0.86076897 0.174408 -0.42905101 0.90239698 -0.039932001 -0.60717899 0.78112203 0.145541
		 -0.587084 0.709773 0.38929901 -0.460531 0.79809499 0.388531 -0.47818199 0.86076897
		 0.174408 -0.587084 0.709773 0.38929901 -0.49293101 0.62145001 0.60895002 -0.377823
		 0.72050899 0.58147699 -0.460531 0.79809499 0.388531 -0.49293101 0.62145001 0.60895002
		 -0.33393401 0.52479702 0.78299201 -0.238157 0.635607 0.73435998 -0.377823 0.72050899
		 0.58147699 -0.33393401 0.52479702 0.78299201 -0.12565801 0.42927599 0.89438897 -0.055202
		 0.5517 0.832214 -0.238157 0.635607 0.73435998 -0.12565801 0.42927599 0.89438897 0.111509
		 0.34423801 0.93223703 0.15313099 0.477 0.86546099 -0.055202 0.5517 0.832214 0.111509
		 0.34423801 0.93223703 0.354352 0.278005 0.89283103 0.36645001 0.41881999 0.83084601
		 0.15313099 0.477 0.86546099 0.354352 0.278005 0.89283103 0.57910001 0.23706201 0.780029
		 0.56387401 0.38285401 0.73175699 0.36645001 0.41881999 0.83084601 0.57910001 0.23706201
		 0.780029 0.76375198 0.225417 0.60487199 0.72607702 0.37262401 0.57789499 0.56387401
		 0.38285401 0.73175699 0.76375198 0.225417 0.60487199 0.89023501 0.24420901 0.384505
		 0.837183 0.38913199 0.38431999 0.72607702 0.37262401 0.57789499 0.89023501 0.24420901
		 0.384505 0.94616598 0.29159799 0.14050201 0.88631397 0.43075901 0.169981 0.837183
		 0.38913199 0.38431999 0.94616598 0.29159799 0.14050201 0.92607099 0.362946 -0.103256
		 0.86866301 0.49343401 -0.044142 0.88631397 0.43075901 0.169981 0.86866301 0.49343401
		 -0.044142 0.78595501 0.57102001 -0.23708899 0.721497 0.67686999 -0.145908 0.79083103
		 0.61182898 0.015841 0.78595501 0.57102001 -0.23708899 0.64628899 0.655922 -0.389972
		 0.60441399 0.74804401 -0.27407101 0.721497 0.67686999 -0.145908 0.64628899 0.655922
		 -0.389972 0.46333399 0.739829 -0.48782599 0.451042 0.81838399 -0.35610199 0.60441399
		 0.74804401 -0.27407101 0.46333399 0.739829 -0.48782599 0.25500101 0.814529 -0.52107298
		 0.27639499 0.88100499 -0.383973 0.451042 0.81838399 -0.35610199 0.25500101 0.814529
		 -0.52107298 0.041682001 0.87270898 -0.486458 0.097567998 0.92977798 -0.35495499 0.27639499
		 0.88100499 -0.383973 0.041682001 0.87270898 -0.486458 -0.155742 0.90867501 -0.38736901
		 -0.067933001 0.95992798 -0.271889 0.097567998 0.92977798 -0.35495499 -0.155742 0.90867501
		 -0.38736901 -0.31794599 0.91890401 -0.23350701 -0.20390899 0.96850401 -0.142905 -0.067933001
		 0.95992798 -0.271889 -0.31794599 0.91890401 -0.23350701 -0.42905101 0.90239698 -0.039932001
		 -0.29705 0.95466602 0.019370001 -0.20390899 0.96850401 -0.142905 -0.42905101 0.90239698
		 -0.039932001 -0.47818199 0.86076897 0.174408 -0.33823699 0.91976899 0.19905201 -0.29705
		 0.95466602 0.019370001 -0.47818199 0.86076897 0.174408 -0.460531 0.79809499 0.388531
		 -0.323439 0.86722797 0.378553 -0.33823699 0.91976899 0.19905201 -0.460531 0.79809499
		 0.388531 -0.377823 0.72050899 0.58147699;
	setAttr ".n[1162:1327]" -type "float3"  -0.254105 0.80218798 0.54030102 -0.323439
		 0.86722797 0.378553 -0.377823 0.72050899 0.58147699 -0.238157 0.635607 0.73435998
		 -0.137022 0.73101401 0.66846299 -0.254105 0.80218798 0.54030102 -0.238157 0.635607
		 0.73435998 -0.055202 0.5517 0.832214 0.016349999 0.66067398 0.75049502 -0.137022
		 0.73101401 0.66846299 -0.055202 0.5517 0.832214 0.15313099 0.477 0.86546099 0.190997
		 0.59805202 0.77836603 0.016349999 0.66067398 0.75049502 0.15313099 0.477 0.86546099
		 0.36645001 0.41881999 0.83084601 0.36982399 0.54927897 0.74934798 0.190997 0.59805202
		 0.77836603 0.36645001 0.41881999 0.83084601 0.56387401 0.38285401 0.73175699 0.53532499
		 0.51912898 0.666282 0.36982399 0.54927897 0.74934798 0.56387401 0.38285401 0.73175699
		 0.72607702 0.37262401 0.57789499 0.67130202 0.51055402 0.53729802 0.53532499 0.51912898
		 0.666282 0.72607702 0.37262401 0.57789499 0.837183 0.38913199 0.38431999 0.76444203
		 0.52439201 0.37502301 0.67130202 0.51055402 0.53729802 0.837183 0.38913199 0.38431999
		 0.88631397 0.43075901 0.169981 0.80562901 0.55928898 0.19534101 0.76444203 0.52439201
		 0.37502301 0.88631397 0.43075901 0.169981 0.86866301 0.49343401 -0.044142 0.79083103
		 0.61182898 0.015841 0.80562901 0.55928898 0.19534101 0.79083103 0.61182898 0.015841
		 0.721497 0.67686999 -0.145908 0.64058298 0.76612997 -0.051940002 0.69501197 0.71507198
		 0.075037003 0.721497 0.67686999 -0.145908 0.60441399 0.74804401 -0.27407101 0.54866999
		 0.82200402 -0.152551 0.64058298 0.76612997 -0.051940002 0.60441399 0.74804401 -0.27407101
		 0.451042 0.81838399 -0.35610199 0.428269 0.87722301 -0.216948 0.54866999 0.82200402
		 -0.152551 0.451042 0.81838399 -0.35610199 0.27639499 0.88100499 -0.383973 0.29116601
		 0.92638201 -0.23882701 0.428269 0.87722301 -0.216948 0.27639499 0.88100499 -0.383973
		 0.097567998 0.92977798 -0.35495499 0.150783 0.96467 -0.216047 0.29116601 0.92638201
		 -0.23882701 0.097567998 0.92977798 -0.35495499 -0.067933001 0.95992798 -0.271889
		 0.02086 0.98833799 -0.150838 0.150783 0.96467 -0.216047 -0.067933001 0.95992798 -0.271889
		 -0.20390899 0.96850401 -0.142905 -0.085885003 0.99507099 -0.049582001 0.02086 0.98833799
		 -0.150838 -0.20390899 0.96850401 -0.142905 -0.29705 0.95466602 0.019370001 -0.159003
		 0.98420697 0.077808 -0.085885003 0.99507099 -0.049582001 -0.29705 0.95466602 0.019370001
		 -0.33823699 0.91976899 0.19905201 -0.19133601 0.95681202 0.218863 -0.159003 0.98420697
		 0.077808 -0.33823699 0.91976899 0.19905201 -0.323439 0.86722797 0.378553 -0.179719
		 0.91556698 0.35977599 -0.19133601 0.95681202 0.218863 -0.323439 0.86722797 0.378553
		 -0.254105 0.80218798 0.54030102 -0.12529001 0.86450797 0.486752 -0.179719 0.91556698
		 0.35977599 -0.254105 0.80218798 0.54030102 -0.137022 0.73101401 0.66846299 -0.033376999
		 0.808635 0.587363 -0.12529001 0.86450797 0.486752 -0.137022 0.73101401 0.66846299
		 0.016349999 0.66067398 0.75049502 0.087024003 0.753416 0.65175998 -0.033376999 0.808635
		 0.587363 0.016349999 0.66067398 0.75049502 0.190997 0.59805202 0.77836603 0.224126
		 0.704256 0.67364001 0.087024003 0.753416 0.65175998 0.190997 0.59805202 0.77836603
		 0.36982399 0.54927897 0.74934798 0.36451 0.66596901 0.65086001 0.224126 0.704256
		 0.67364001 0.36982399 0.54927897 0.74934798 0.53532499 0.51912898 0.666282 0.49443299
		 0.64230001 0.58565003 0.36451 0.66596901 0.65086001 0.53532499 0.51912898 0.666282
		 0.67130202 0.51055402 0.53729802 0.60117799 0.63556802 0.484395 0.49443299 0.64230001
		 0.58565003 0.67130202 0.51055402 0.53729802 0.76444203 0.52439201 0.37502301 0.67429602
		 0.64643103 0.35700399 0.60117799 0.63556802 0.484395 0.76444203 0.52439201 0.37502301
		 0.80562901 0.55928898 0.19534101 0.70662898 0.67382598 0.215949 0.67429602 0.64643103
		 0.35700399 0.80562901 0.55928898 0.19534101 0.79083103 0.61182898 0.015841 0.69501197
		 0.71507198 0.075037003 0.70662898 0.67382598 0.215949 0.69501197 0.71507198 0.075037003
		 0.64058298 0.76612997 -0.051940002 0.54665297 0.83633298 0.041443001 0.58522201 0.80015302
		 0.13142 0.64058298 0.76612997 -0.051940002 0.54866999 0.82200402 -0.152551 0.48152301
		 0.875925 -0.029851001 0.54665297 0.83633298 0.041443001 0.54866999 0.82200402 -0.152551
		 0.428269 0.87722301 -0.216948 0.39620599 0.91505402 -0.075482003 0.48152301 0.875925
		 -0.029851001 0.428269 0.87722301 -0.216948 0.29116601 0.92638201 -0.23882701 0.299054
		 0.949889 -0.090985999 0.39620599 0.91505402 -0.075482003 0.29116601 0.92638201 -0.23882701
		 0.150783 0.96467 -0.216047 0.199577 0.97702003 -0.074844003 0.299054 0.949889 -0.090985999
		 0.150783 0.96467 -0.216047 0.02086 0.98833799 -0.150838 0.107513 0.99379098 -0.028636999
		 0.199577 0.97702003 -0.074844003 0.02086 0.98833799 -0.150838 -0.085885003 0.99507099
		 -0.049582001 0.031872001 0.99856198 0.043113999 0.107513 0.99379098 -0.028636999
		 -0.085885003 0.99507099 -0.049582001 -0.159003 0.98420697 0.077808 -0.019939 0.99086398
		 0.13338301 0.031872001 0.99856198 0.043113999 -0.159003 0.98420697 0.077808 -0.19133601
		 0.95681202 0.218863 -0.042851001 0.971452 0.233336 -0.019939 0.99086398 0.13338301
		 -0.19133601 0.95681202 0.218863 -0.179719 0.91556698 0.35977599 -0.034619 0.94222498
		 0.333188 -0.042851001 0.971452 0.233336 -0.179719 0.91556698 0.35977599 -0.12529001
		 0.86450797 0.486752 0.0039499998 0.90604502 0.42316401 -0.034619 0.94222498 0.333188
		 -0.12529001 0.86450797 0.486752 -0.033376999 0.808635 0.587363 0.069080003 0.86645198
		 0.49445799 0.0039499998 0.90604502 0.42316401;
	setAttr ".n[1328:1493]" -type "float3"  -0.033376999 0.808635 0.587363 0.087024003
		 0.753416 0.65175998 0.154397 0.82732302 0.54009002 0.069080003 0.86645198 0.49445799
		 0.087024003 0.753416 0.65175998 0.224126 0.704256 0.67364001 0.25154901 0.79248899
		 0.55559403 0.154397 0.82732302 0.54009002 0.224126 0.704256 0.67364001 0.36451 0.66596901
		 0.65086001 0.351026 0.76535797 0.53945202 0.25154901 0.79248899 0.55559403 0.36451
		 0.66596901 0.65086001 0.49443299 0.64230001 0.58565003 0.44308999 0.748586 0.49324399
		 0.351026 0.76535797 0.53945202 0.49443299 0.64230001 0.58565003 0.60117799 0.63556802
		 0.484395 0.51872998 0.74381602 0.42149401 0.44308999 0.748586 0.49324399 0.60117799
		 0.63556802 0.484395 0.67429602 0.64643103 0.35700399 0.57054198 0.751513 0.33122399
		 0.51872998 0.74381602 0.42149401 0.67429602 0.64643103 0.35700399 0.70662898 0.67382598
		 0.215949 0.59345299 0.770926 0.231272 0.57054198 0.751513 0.33122399 0.70662898 0.67382598
		 0.215949 0.69501197 0.71507198 0.075037003 0.58522201 0.80015302 0.13142 0.59345299
		 0.770926 0.231272 0.58522201 0.80015302 0.13142 0.54665297 0.83633298 0.041443001
		 0.449092 0.88444501 0.126782 0.472258 0.86271298 0.18082599 0.54665297 0.83633298
		 0.041443001 0.48152301 0.875925 -0.029851001 0.40997201 0.90822601 0.083959997 0.449092
		 0.88444501 0.126782 0.48152301 0.875925 -0.029851001 0.39620599 0.91505402 -0.075482003
		 0.35872701 0.93172801 0.056552 0.40997201 0.90822601 0.083959997 0.39620599 0.91505402
		 -0.075482003 0.299054 0.949889 -0.090985999 0.30037299 0.95265102 0.047239002 0.35872701
		 0.93172801 0.056552 0.299054 0.949889 -0.090985999 0.199577 0.97702003 -0.074844003
		 0.240623 0.96894699 0.056935001 0.30037299 0.95265102 0.047239002 0.199577 0.97702003
		 -0.074844003 0.107513 0.99379098 -0.028636999 0.185325 0.97902101 0.084688999 0.240623
		 0.96894699 0.056935001 0.107513 0.99379098 -0.028636999 0.031872001 0.99856198 0.043113999
		 0.139893 0.98188603 0.127786 0.185325 0.97902101 0.084688999 0.031872001 0.99856198
		 0.043113999 -0.019939 0.99086398 0.13338301 0.108772 0.97726297 0.182005 0.139893
		 0.98188603 0.127786 -0.019939 0.99086398 0.13338301 -0.042851001 0.971452 0.233336
		 0.095011003 0.96560299 0.24204101 0.108772 0.97726297 0.182005 -0.042851001 0.971452
		 0.233336 -0.034619 0.94222498 0.333188 0.099955 0.948048 0.302017 0.095011003 0.96560299
		 0.24204101 -0.034619 0.94222498 0.333188 0.0039499998 0.90604502 0.42316401 0.123121
		 0.92631698 0.35606 0.099955 0.948048 0.302017 0.0039499998 0.90604502 0.42316401
		 0.069080003 0.86645198 0.49445799 0.162241 0.90253597 0.398882 0.123121 0.92631698
		 0.35606 0.069080003 0.86645198 0.49445799 0.154397 0.82732302 0.54009002 0.213486
		 0.87903398 0.42629001 0.162241 0.90253597 0.398882 0.154397 0.82732302 0.54009002
		 0.25154901 0.79248899 0.55559403 0.27184001 0.85811001 0.43560201 0.213486 0.87903398
		 0.42629001 0.25154901 0.79248899 0.55559403 0.351026 0.76535797 0.53945202 0.33159
		 0.84181398 0.42590699 0.27184001 0.85811001 0.43560201 0.351026 0.76535797 0.53945202
		 0.44308999 0.748586 0.49324399 0.386888 0.83174002 0.39815301 0.33159 0.84181398
		 0.42590699 0.44308999 0.748586 0.49324399 0.51872998 0.74381602 0.42149401 0.43232
		 0.82887501 0.35505599 0.386888 0.83174002 0.39815301 0.51872998 0.74381602 0.42149401
		 0.57054198 0.751513 0.33122399 0.46344101 0.83349901 0.30083701 0.43232 0.82887501
		 0.35505599 0.57054198 0.751513 0.33122399 0.59345299 0.770926 0.231272 0.477202 0.84515899
		 0.240802 0.46344101 0.83349901 0.30083701 0.59345299 0.770926 0.231272 0.58522201
		 0.80015302 0.13142 0.472258 0.86271298 0.18082599 0.477202 0.84515899 0.240802 -0.123121
		 -0.92631602 -0.35606 -0.099955 -0.948048 -0.302017 -0.29202801 -0.92412001 -0.246418
		 -0.162241 -0.90253597 -0.398882 -0.123121 -0.92631602 -0.35606 -0.29202801 -0.92412001
		 -0.246418 -0.213486 -0.87903398 -0.42629001 -0.162241 -0.90253597 -0.398882 -0.29202801
		 -0.92412001 -0.246418 -0.27184001 -0.85811001 -0.43560299 -0.213486 -0.87903398 -0.42629001
		 -0.29202801 -0.92412001 -0.246418 -0.33159 -0.84181398 -0.425908 -0.27184001 -0.85811001
		 -0.43560299 -0.29202801 -0.92412001 -0.246418 -0.386888 -0.83174002 -0.39815301 -0.33159
		 -0.84181398 -0.425908 -0.29202801 -0.92412001 -0.246418 -0.43232 -0.82887501 -0.355057
		 -0.386888 -0.83174002 -0.39815301 -0.29202801 -0.92412001 -0.246418 -0.46344 -0.83349901
		 -0.30083701 -0.43232 -0.82887501 -0.355057 -0.29202801 -0.92412001 -0.246418 -0.477202
		 -0.84515899 -0.24080101 -0.46344 -0.83349901 -0.30083701 -0.29202801 -0.92412001
		 -0.246418 -0.472258 -0.86271399 -0.18082599 -0.477202 -0.84515899 -0.24080101 -0.29202801
		 -0.92412001 -0.246418 -0.449092 -0.88444501 -0.126782 -0.472258 -0.86271399 -0.18082599
		 -0.29202801 -0.92412001 -0.246418 -0.40997201 -0.90822601 -0.083959997 -0.449092
		 -0.88444501 -0.126782 -0.29202801 -0.92412001 -0.246418 -0.35872701 -0.93172801 -0.056552
		 -0.40997201 -0.90822601 -0.083959997 -0.29202801 -0.92412001 -0.246418 -0.30037299
		 -0.95265102 -0.04724 -0.35872701 -0.93172801 -0.056552 -0.29202801 -0.92412001 -0.246418
		 -0.240623 -0.96894699 -0.056935001 -0.30037299 -0.95265102 -0.04724 -0.29202801 -0.92412001
		 -0.246418 -0.185325 -0.97902101 -0.084688999 -0.240623 -0.96894699 -0.056935001 -0.29202801
		 -0.92412001 -0.246418 -0.139893 -0.98188603 -0.127786 -0.185325 -0.97902101 -0.084688999
		 -0.29202801 -0.92412001 -0.246418 -0.108772 -0.97726297 -0.182005 -0.139893 -0.98188603
		 -0.127786 -0.29202801 -0.92412001 -0.246418;
	setAttr ".n[1494:1559]" -type "float3"  -0.095011003 -0.96560299 -0.24204101
		 -0.108772 -0.97726297 -0.182005 -0.29202801 -0.92412001 -0.246418 -0.099955 -0.948048
		 -0.302017 -0.095011003 -0.96560299 -0.24204101 -0.29202801 -0.92412001 -0.246418
		 0.472258 0.86271298 0.18082599 0.449092 0.88444501 0.126782 0.29202801 0.92412001
		 0.246418 0.449092 0.88444501 0.126782 0.40997201 0.90822601 0.083959997 0.29202801
		 0.92412001 0.246418 0.40997201 0.90822601 0.083959997 0.35872701 0.93172801 0.056552
		 0.29202801 0.92412001 0.246418 0.35872701 0.93172801 0.056552 0.30037299 0.95265102
		 0.047239002 0.29202801 0.92412001 0.246418 0.30037299 0.95265102 0.047239002 0.240623
		 0.96894699 0.056935001 0.29202801 0.92412001 0.246418 0.240623 0.96894699 0.056935001
		 0.185325 0.97902101 0.084688999 0.29202801 0.92412001 0.246418 0.185325 0.97902101
		 0.084688999 0.139893 0.98188603 0.127786 0.29202801 0.92412001 0.246418 0.139893
		 0.98188603 0.127786 0.108772 0.97726297 0.182005 0.29202801 0.92412001 0.246418 0.108772
		 0.97726297 0.182005 0.095011003 0.96560299 0.24204101 0.29202801 0.92412001 0.246418
		 0.095011003 0.96560299 0.24204101 0.099955 0.948048 0.302017 0.29202801 0.92412001
		 0.246418 0.099955 0.948048 0.302017 0.123121 0.92631698 0.35606 0.29202801 0.92412001
		 0.246418 0.123121 0.92631698 0.35606 0.162241 0.90253597 0.398882 0.29202801 0.92412001
		 0.246418 0.162241 0.90253597 0.398882 0.213486 0.87903398 0.42629001 0.29202801 0.92412001
		 0.246418 0.213486 0.87903398 0.42629001 0.27184001 0.85811001 0.43560201 0.29202801
		 0.92412001 0.246418 0.27184001 0.85811001 0.43560201 0.33159 0.84181398 0.42590699
		 0.29202801 0.92412001 0.246418 0.33159 0.84181398 0.42590699 0.386888 0.83174002
		 0.39815301 0.29202801 0.92412001 0.246418 0.386888 0.83174002 0.39815301 0.43232
		 0.82887501 0.35505599 0.29202801 0.92412001 0.246418 0.43232 0.82887501 0.35505599
		 0.46344101 0.83349901 0.30083701 0.29202801 0.92412001 0.246418 0.46344101 0.83349901
		 0.30083701 0.477202 0.84515899 0.240802 0.29202801 0.92412001 0.246418 0.477202 0.84515899
		 0.240802 0.472258 0.86271298 0.18082599 0.29202801 0.92412001 0.246418;
	setAttr -s 400 -ch 1560 ".fc[0:399]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 4 5 6 -2
		mu 0 4 1 4 5 2
		f 4 7 8 9 -6
		mu 0 4 4 6 7 5
		f 4 10 11 12 -9
		mu 0 4 6 8 9 7
		f 4 13 14 15 -12
		mu 0 4 8 10 11 9
		f 4 16 17 18 -15
		mu 0 4 10 12 13 11
		f 4 19 20 21 -18
		mu 0 4 12 14 15 13
		f 4 22 23 24 -21
		mu 0 4 14 16 17 15
		f 4 25 26 27 -24
		mu 0 4 16 18 19 17
		f 4 28 29 30 -27
		mu 0 4 18 20 21 19
		f 4 31 32 33 -30
		mu 0 4 20 22 23 21
		f 4 34 35 36 -33
		mu 0 4 22 24 25 23
		f 4 37 38 39 -36
		mu 0 4 24 26 27 25
		f 4 40 41 42 -39
		mu 0 4 26 28 29 27
		f 4 43 44 45 -42
		mu 0 4 28 30 31 29
		f 4 46 47 48 -45
		mu 0 4 30 32 33 31
		f 4 49 50 51 -48
		mu 0 4 32 34 35 33
		f 4 52 53 54 -51
		mu 0 4 34 36 37 35
		f 4 55 56 57 -54
		mu 0 4 36 38 39 37
		f 4 58 -4 59 -57
		mu 0 4 38 40 41 39
		f 4 -3 60 61 62
		mu 0 4 3 2 42 43
		f 4 -7 63 64 -61
		mu 0 4 2 5 44 42
		f 4 -10 65 66 -64
		mu 0 4 5 7 45 44
		f 4 -13 67 68 -66
		mu 0 4 7 9 46 45
		f 4 -16 69 70 -68
		mu 0 4 9 11 47 46
		f 4 -19 71 72 -70
		mu 0 4 11 13 48 47
		f 4 -22 73 74 -72
		mu 0 4 13 15 49 48
		f 4 -25 75 76 -74
		mu 0 4 15 17 50 49
		f 4 -28 77 78 -76
		mu 0 4 17 19 51 50
		f 4 -31 79 80 -78
		mu 0 4 19 21 52 51
		f 4 -34 81 82 -80
		mu 0 4 21 23 53 52
		f 4 -37 83 84 -82
		mu 0 4 23 25 54 53
		f 4 -40 85 86 -84
		mu 0 4 25 27 55 54
		f 4 -43 87 88 -86
		mu 0 4 27 29 56 55
		f 4 -46 89 90 -88
		mu 0 4 29 31 57 56
		f 4 -49 91 92 -90
		mu 0 4 31 33 58 57
		f 4 -52 93 94 -92
		mu 0 4 33 35 59 58
		f 4 -55 95 96 -94
		mu 0 4 35 37 60 59
		f 4 -58 97 98 -96
		mu 0 4 37 39 61 60
		f 4 -60 -63 99 -98
		mu 0 4 39 41 62 61
		f 4 -62 100 101 102
		mu 0 4 43 42 63 64
		f 4 -65 103 104 -101
		mu 0 4 42 44 65 63
		f 4 -67 105 106 -104
		mu 0 4 44 45 66 65
		f 4 -69 107 108 -106
		mu 0 4 45 46 67 66
		f 4 -71 109 110 -108
		mu 0 4 46 47 68 67
		f 4 -73 111 112 -110
		mu 0 4 47 48 69 68
		f 4 -75 113 114 -112
		mu 0 4 48 49 70 69
		f 4 -77 115 116 -114
		mu 0 4 49 50 71 70
		f 4 -79 117 118 -116
		mu 0 4 50 51 72 71
		f 4 -81 119 120 -118
		mu 0 4 51 52 73 72
		f 4 -83 121 122 -120
		mu 0 4 52 53 74 73
		f 4 -85 123 124 -122
		mu 0 4 53 54 75 74
		f 4 -87 125 126 -124
		mu 0 4 54 55 76 75
		f 4 -89 127 128 -126
		mu 0 4 55 56 77 76
		f 4 -91 129 130 -128
		mu 0 4 56 57 78 77
		f 4 -93 131 132 -130
		mu 0 4 57 58 79 78
		f 4 -95 133 134 -132
		mu 0 4 58 59 80 79
		f 4 -97 135 136 -134
		mu 0 4 59 60 81 80
		f 4 -99 137 138 -136
		mu 0 4 60 61 82 81
		f 4 -100 -103 139 -138
		mu 0 4 61 62 83 82
		f 4 -102 140 141 142
		mu 0 4 64 63 84 85
		f 4 -105 143 144 -141
		mu 0 4 63 65 86 84
		f 4 -107 145 146 -144
		mu 0 4 65 66 87 86
		f 4 -109 147 148 -146
		mu 0 4 66 67 88 87
		f 4 -111 149 150 -148
		mu 0 4 67 68 89 88
		f 4 -113 151 152 -150
		mu 0 4 68 69 90 89
		f 4 -115 153 154 -152
		mu 0 4 69 70 91 90
		f 4 -117 155 156 -154
		mu 0 4 70 71 92 91
		f 4 -119 157 158 -156
		mu 0 4 71 72 93 92
		f 4 -121 159 160 -158
		mu 0 4 72 73 94 93
		f 4 -123 161 162 -160
		mu 0 4 73 74 95 94
		f 4 -125 163 164 -162
		mu 0 4 74 75 96 95
		f 4 -127 165 166 -164
		mu 0 4 75 76 97 96
		f 4 -129 167 168 -166
		mu 0 4 76 77 98 97
		f 4 -131 169 170 -168
		mu 0 4 77 78 99 98
		f 4 -133 171 172 -170
		mu 0 4 78 79 100 99
		f 4 -135 173 174 -172
		mu 0 4 79 80 101 100
		f 4 -137 175 176 -174
		mu 0 4 80 81 102 101
		f 4 -139 177 178 -176
		mu 0 4 81 82 103 102
		f 4 -140 -143 179 -178
		mu 0 4 82 83 104 103
		f 4 -142 180 181 182
		mu 0 4 85 84 105 106
		f 4 -145 183 184 -181
		mu 0 4 84 86 107 105
		f 4 -147 185 186 -184
		mu 0 4 86 87 108 107
		f 4 -149 187 188 -186
		mu 0 4 87 88 109 108
		f 4 -151 189 190 -188
		mu 0 4 88 89 110 109
		f 4 -153 191 192 -190
		mu 0 4 89 90 111 110
		f 4 -155 193 194 -192
		mu 0 4 90 91 112 111
		f 4 -157 195 196 -194
		mu 0 4 91 92 113 112
		f 4 -159 197 198 -196
		mu 0 4 92 93 114 113
		f 4 -161 199 200 -198
		mu 0 4 93 94 115 114
		f 4 -163 201 202 -200
		mu 0 4 94 95 116 115
		f 4 -165 203 204 -202
		mu 0 4 95 96 117 116
		f 4 -167 205 206 -204
		mu 0 4 96 97 118 117
		f 4 -169 207 208 -206
		mu 0 4 97 98 119 118
		f 4 -171 209 210 -208
		mu 0 4 98 99 120 119
		f 4 -173 211 212 -210
		mu 0 4 99 100 121 120
		f 4 -175 213 214 -212
		mu 0 4 100 101 122 121
		f 4 -177 215 216 -214
		mu 0 4 101 102 123 122
		f 4 -179 217 218 -216
		mu 0 4 102 103 124 123
		f 4 -180 -183 219 -218
		mu 0 4 103 104 125 124
		f 4 -182 220 221 222
		mu 0 4 106 105 126 127
		f 4 -185 223 224 -221
		mu 0 4 105 107 128 126
		f 4 -187 225 226 -224
		mu 0 4 107 108 129 128
		f 4 -189 227 228 -226
		mu 0 4 108 109 130 129
		f 4 -191 229 230 -228
		mu 0 4 109 110 131 130
		f 4 -193 231 232 -230
		mu 0 4 110 111 132 131
		f 4 -195 233 234 -232
		mu 0 4 111 112 133 132
		f 4 -197 235 236 -234
		mu 0 4 112 113 134 133
		f 4 -199 237 238 -236
		mu 0 4 113 114 135 134
		f 4 -201 239 240 -238
		mu 0 4 114 115 136 135
		f 4 -203 241 242 -240
		mu 0 4 115 116 137 136
		f 4 -205 243 244 -242
		mu 0 4 116 117 138 137
		f 4 -207 245 246 -244
		mu 0 4 117 118 139 138
		f 4 -209 247 248 -246
		mu 0 4 118 119 140 139
		f 4 -211 249 250 -248
		mu 0 4 119 120 141 140
		f 4 -213 251 252 -250
		mu 0 4 120 121 142 141
		f 4 -215 253 254 -252
		mu 0 4 121 122 143 142
		f 4 -217 255 256 -254
		mu 0 4 122 123 144 143
		f 4 -219 257 258 -256
		mu 0 4 123 124 145 144
		f 4 -220 -223 259 -258
		mu 0 4 124 125 146 145
		f 4 -222 260 261 262
		mu 0 4 127 126 147 148
		f 4 -225 263 264 -261
		mu 0 4 126 128 149 147
		f 4 -227 265 266 -264
		mu 0 4 128 129 150 149
		f 4 -229 267 268 -266
		mu 0 4 129 130 151 150
		f 4 -231 269 270 -268
		mu 0 4 130 131 152 151
		f 4 -233 271 272 -270
		mu 0 4 131 132 153 152
		f 4 -235 273 274 -272
		mu 0 4 132 133 154 153
		f 4 -237 275 276 -274
		mu 0 4 133 134 155 154
		f 4 -239 277 278 -276
		mu 0 4 134 135 156 155
		f 4 -241 279 280 -278
		mu 0 4 135 136 157 156
		f 4 -243 281 282 -280
		mu 0 4 136 137 158 157
		f 4 -245 283 284 -282
		mu 0 4 137 138 159 158
		f 4 -247 285 286 -284
		mu 0 4 138 139 160 159
		f 4 -249 287 288 -286
		mu 0 4 139 140 161 160
		f 4 -251 289 290 -288
		mu 0 4 140 141 162 161
		f 4 -253 291 292 -290
		mu 0 4 141 142 163 162
		f 4 -255 293 294 -292
		mu 0 4 142 143 164 163
		f 4 -257 295 296 -294
		mu 0 4 143 144 165 164
		f 4 -259 297 298 -296
		mu 0 4 144 145 166 165
		f 4 -260 -263 299 -298
		mu 0 4 145 146 167 166
		f 4 -262 300 301 302
		mu 0 4 148 147 168 169
		f 4 -265 303 304 -301
		mu 0 4 147 149 170 168
		f 4 -267 305 306 -304
		mu 0 4 149 150 171 170
		f 4 -269 307 308 -306
		mu 0 4 150 151 172 171
		f 4 -271 309 310 -308
		mu 0 4 151 152 173 172
		f 4 -273 311 312 -310
		mu 0 4 152 153 174 173
		f 4 -275 313 314 -312
		mu 0 4 153 154 175 174
		f 4 -277 315 316 -314
		mu 0 4 154 155 176 175
		f 4 -279 317 318 -316
		mu 0 4 155 156 177 176
		f 4 -281 319 320 -318
		mu 0 4 156 157 178 177
		f 4 -283 321 322 -320
		mu 0 4 157 158 179 178
		f 4 -285 323 324 -322
		mu 0 4 158 159 180 179
		f 4 -287 325 326 -324
		mu 0 4 159 160 181 180
		f 4 -289 327 328 -326
		mu 0 4 160 161 182 181
		f 4 -291 329 330 -328
		mu 0 4 161 162 183 182
		f 4 -293 331 332 -330
		mu 0 4 162 163 184 183
		f 4 -295 333 334 -332
		mu 0 4 163 164 185 184
		f 4 -297 335 336 -334
		mu 0 4 164 165 186 185
		f 4 -299 337 338 -336
		mu 0 4 165 166 187 186
		f 4 -300 -303 339 -338
		mu 0 4 166 167 188 187
		f 4 -302 340 341 342
		mu 0 4 169 168 189 190
		f 4 -305 343 344 -341
		mu 0 4 168 170 191 189
		f 4 -307 345 346 -344
		mu 0 4 170 171 192 191
		f 4 -309 347 348 -346
		mu 0 4 171 172 193 192
		f 4 -311 349 350 -348
		mu 0 4 172 173 194 193
		f 4 -313 351 352 -350
		mu 0 4 173 174 195 194
		f 4 -315 353 354 -352
		mu 0 4 174 175 196 195
		f 4 -317 355 356 -354
		mu 0 4 175 176 197 196
		f 4 -319 357 358 -356
		mu 0 4 176 177 198 197
		f 4 -321 359 360 -358
		mu 0 4 177 178 199 198
		f 4 -323 361 362 -360
		mu 0 4 178 179 200 199
		f 4 -325 363 364 -362
		mu 0 4 179 180 201 200
		f 4 -327 365 366 -364
		mu 0 4 180 181 202 201
		f 4 -329 367 368 -366
		mu 0 4 181 182 203 202
		f 4 -331 369 370 -368
		mu 0 4 182 183 204 203
		f 4 -333 371 372 -370
		mu 0 4 183 184 205 204
		f 4 -335 373 374 -372
		mu 0 4 184 185 206 205
		f 4 -337 375 376 -374
		mu 0 4 185 186 207 206
		f 4 -339 377 378 -376
		mu 0 4 186 187 208 207
		f 4 -340 -343 379 -378
		mu 0 4 187 188 209 208
		f 4 -342 380 381 382
		mu 0 4 190 189 210 211
		f 4 -345 383 384 -381
		mu 0 4 189 191 212 210
		f 4 -347 385 386 -384
		mu 0 4 191 192 213 212
		f 4 -349 387 388 -386
		mu 0 4 192 193 214 213
		f 4 -351 389 390 -388
		mu 0 4 193 194 215 214
		f 4 -353 391 392 -390
		mu 0 4 194 195 216 215
		f 4 -355 393 394 -392
		mu 0 4 195 196 217 216
		f 4 -357 395 396 -394
		mu 0 4 196 197 218 217
		f 4 -359 397 398 -396
		mu 0 4 197 198 219 218
		f 4 -361 399 400 -398
		mu 0 4 198 199 220 219
		f 4 -363 401 402 -400
		mu 0 4 199 200 221 220
		f 4 -365 403 404 -402
		mu 0 4 200 201 222 221
		f 4 -367 405 406 -404
		mu 0 4 201 202 223 222
		f 4 -369 407 408 -406
		mu 0 4 202 203 224 223
		f 4 -371 409 410 -408
		mu 0 4 203 204 225 224
		f 4 -373 411 412 -410
		mu 0 4 204 205 226 225
		f 4 -375 413 414 -412
		mu 0 4 205 206 227 226
		f 4 -377 415 416 -414
		mu 0 4 206 207 228 227
		f 4 -379 417 418 -416
		mu 0 4 207 208 229 228
		f 4 -380 -383 419 -418
		mu 0 4 208 209 230 229
		f 4 -382 420 421 422
		mu 0 4 211 210 231 232
		f 4 -385 423 424 -421
		mu 0 4 210 212 233 231
		f 4 -387 425 426 -424
		mu 0 4 212 213 234 233
		f 4 -389 427 428 -426
		mu 0 4 213 214 235 234
		f 4 -391 429 430 -428
		mu 0 4 214 215 236 235
		f 4 -393 431 432 -430
		mu 0 4 215 216 237 236
		f 4 -395 433 434 -432
		mu 0 4 216 217 238 237
		f 4 -397 435 436 -434
		mu 0 4 217 218 239 238
		f 4 -399 437 438 -436
		mu 0 4 218 219 240 239
		f 4 -401 439 440 -438
		mu 0 4 219 220 241 240
		f 4 -403 441 442 -440
		mu 0 4 220 221 242 241
		f 4 -405 443 444 -442
		mu 0 4 221 222 243 242
		f 4 -407 445 446 -444
		mu 0 4 222 223 244 243
		f 4 -409 447 448 -446
		mu 0 4 223 224 245 244
		f 4 -411 449 450 -448
		mu 0 4 224 225 246 245
		f 4 -413 451 452 -450
		mu 0 4 225 226 247 246
		f 4 -415 453 454 -452
		mu 0 4 226 227 248 247
		f 4 -417 455 456 -454
		mu 0 4 227 228 249 248
		f 4 -419 457 458 -456
		mu 0 4 228 229 250 249
		f 4 -420 -423 459 -458
		mu 0 4 229 230 251 250
		f 4 -422 460 461 462
		mu 0 4 232 231 252 253
		f 4 -425 463 464 -461
		mu 0 4 231 233 254 252
		f 4 -427 465 466 -464
		mu 0 4 233 234 255 254
		f 4 -429 467 468 -466
		mu 0 4 234 235 256 255
		f 4 -431 469 470 -468
		mu 0 4 235 236 257 256
		f 4 -433 471 472 -470
		mu 0 4 236 237 258 257
		f 4 -435 473 474 -472
		mu 0 4 237 238 259 258
		f 4 -437 475 476 -474
		mu 0 4 238 239 260 259
		f 4 -439 477 478 -476
		mu 0 4 239 240 261 260
		f 4 -441 479 480 -478
		mu 0 4 240 241 262 261
		f 4 -443 481 482 -480
		mu 0 4 241 242 263 262
		f 4 -445 483 484 -482
		mu 0 4 242 243 264 263
		f 4 -447 485 486 -484
		mu 0 4 243 244 265 264
		f 4 -449 487 488 -486
		mu 0 4 244 245 266 265
		f 4 -451 489 490 -488
		mu 0 4 245 246 267 266
		f 4 -453 491 492 -490
		mu 0 4 246 247 268 267
		f 4 -455 493 494 -492
		mu 0 4 247 248 269 268
		f 4 -457 495 496 -494
		mu 0 4 248 249 270 269
		f 4 -459 497 498 -496
		mu 0 4 249 250 271 270
		f 4 -460 -463 499 -498
		mu 0 4 250 251 272 271
		f 4 -462 500 501 502
		mu 0 4 253 252 273 274
		f 4 -465 503 504 -501
		mu 0 4 252 254 275 273
		f 4 -467 505 506 -504
		mu 0 4 254 255 276 275
		f 4 -469 507 508 -506
		mu 0 4 255 256 277 276
		f 4 -471 509 510 -508
		mu 0 4 256 257 278 277
		f 4 -473 511 512 -510
		mu 0 4 257 258 279 278
		f 4 -475 513 514 -512
		mu 0 4 258 259 280 279
		f 4 -477 515 516 -514
		mu 0 4 259 260 281 280
		f 4 -479 517 518 -516
		mu 0 4 260 261 282 281
		f 4 -481 519 520 -518
		mu 0 4 261 262 283 282
		f 4 -483 521 522 -520
		mu 0 4 262 263 284 283
		f 4 -485 523 524 -522
		mu 0 4 263 264 285 284
		f 4 -487 525 526 -524
		mu 0 4 264 265 286 285
		f 4 -489 527 528 -526
		mu 0 4 265 266 287 286
		f 4 -491 529 530 -528
		mu 0 4 266 267 288 287
		f 4 -493 531 532 -530
		mu 0 4 267 268 289 288
		f 4 -495 533 534 -532
		mu 0 4 268 269 290 289
		f 4 -497 535 536 -534
		mu 0 4 269 270 291 290
		f 4 -499 537 538 -536
		mu 0 4 270 271 292 291
		f 4 -500 -503 539 -538
		mu 0 4 271 272 293 292
		f 4 -502 540 541 542
		mu 0 4 274 273 294 295
		f 4 -505 543 544 -541
		mu 0 4 273 275 296 294
		f 4 -507 545 546 -544
		mu 0 4 275 276 297 296
		f 4 -509 547 548 -546
		mu 0 4 276 277 298 297
		f 4 -511 549 550 -548
		mu 0 4 277 278 299 298
		f 4 -513 551 552 -550
		mu 0 4 278 279 300 299
		f 4 -515 553 554 -552
		mu 0 4 279 280 301 300
		f 4 -517 555 556 -554
		mu 0 4 280 281 302 301
		f 4 -519 557 558 -556
		mu 0 4 281 282 303 302
		f 4 -521 559 560 -558
		mu 0 4 282 283 304 303
		f 4 -523 561 562 -560
		mu 0 4 283 284 305 304
		f 4 -525 563 564 -562
		mu 0 4 284 285 306 305
		f 4 -527 565 566 -564
		mu 0 4 285 286 307 306
		f 4 -529 567 568 -566
		mu 0 4 286 287 308 307
		f 4 -531 569 570 -568
		mu 0 4 287 288 309 308
		f 4 -533 571 572 -570
		mu 0 4 288 289 310 309
		f 4 -535 573 574 -572
		mu 0 4 289 290 311 310
		f 4 -537 575 576 -574
		mu 0 4 290 291 312 311
		f 4 -539 577 578 -576
		mu 0 4 291 292 313 312
		f 4 -540 -543 579 -578
		mu 0 4 292 293 314 313
		f 4 -542 580 581 582
		mu 0 4 295 294 315 316
		f 4 -545 583 584 -581
		mu 0 4 294 296 317 315
		f 4 -547 585 586 -584
		mu 0 4 296 297 318 317
		f 4 -549 587 588 -586
		mu 0 4 297 298 319 318
		f 4 -551 589 590 -588
		mu 0 4 298 299 320 319
		f 4 -553 591 592 -590
		mu 0 4 299 300 321 320
		f 4 -555 593 594 -592
		mu 0 4 300 301 322 321
		f 4 -557 595 596 -594
		mu 0 4 301 302 323 322
		f 4 -559 597 598 -596
		mu 0 4 302 303 324 323
		f 4 -561 599 600 -598
		mu 0 4 303 304 325 324
		f 4 -563 601 602 -600
		mu 0 4 304 305 326 325
		f 4 -565 603 604 -602
		mu 0 4 305 306 327 326
		f 4 -567 605 606 -604
		mu 0 4 306 307 328 327
		f 4 -569 607 608 -606
		mu 0 4 307 308 329 328
		f 4 -571 609 610 -608
		mu 0 4 308 309 330 329
		f 4 -573 611 612 -610
		mu 0 4 309 310 331 330
		f 4 -575 613 614 -612
		mu 0 4 310 311 332 331
		f 4 -577 615 616 -614
		mu 0 4 311 312 333 332
		f 4 -579 617 618 -616
		mu 0 4 312 313 334 333
		f 4 -580 -583 619 -618
		mu 0 4 313 314 335 334
		f 4 -582 620 621 622
		mu 0 4 316 315 336 337
		f 4 -585 623 624 -621
		mu 0 4 315 317 338 336
		f 4 -587 625 626 -624
		mu 0 4 317 318 339 338
		f 4 -589 627 628 -626
		mu 0 4 318 319 340 339
		f 4 -591 629 630 -628
		mu 0 4 319 320 341 340
		f 4 -593 631 632 -630
		mu 0 4 320 321 342 341
		f 4 -595 633 634 -632
		mu 0 4 321 322 343 342
		f 4 -597 635 636 -634
		mu 0 4 322 323 344 343
		f 4 -599 637 638 -636
		mu 0 4 323 324 345 344
		f 4 -601 639 640 -638
		mu 0 4 324 325 346 345
		f 4 -603 641 642 -640
		mu 0 4 325 326 347 346
		f 4 -605 643 644 -642
		mu 0 4 326 327 348 347
		f 4 -607 645 646 -644
		mu 0 4 327 328 349 348
		f 4 -609 647 648 -646
		mu 0 4 328 329 350 349
		f 4 -611 649 650 -648
		mu 0 4 329 330 351 350
		f 4 -613 651 652 -650
		mu 0 4 330 331 352 351
		f 4 -615 653 654 -652
		mu 0 4 331 332 353 352
		f 4 -617 655 656 -654
		mu 0 4 332 333 354 353
		f 4 -619 657 658 -656
		mu 0 4 333 334 355 354
		f 4 -620 -623 659 -658
		mu 0 4 334 335 356 355
		f 4 -622 660 661 662
		mu 0 4 337 336 357 358
		f 4 -625 663 664 -661
		mu 0 4 336 338 359 357
		f 4 -627 665 666 -664
		mu 0 4 338 339 360 359
		f 4 -629 667 668 -666
		mu 0 4 339 340 361 360
		f 4 -631 669 670 -668
		mu 0 4 340 341 362 361
		f 4 -633 671 672 -670
		mu 0 4 341 342 363 362
		f 4 -635 673 674 -672
		mu 0 4 342 343 364 363
		f 4 -637 675 676 -674
		mu 0 4 343 344 365 364
		f 4 -639 677 678 -676
		mu 0 4 344 345 366 365
		f 4 -641 679 680 -678
		mu 0 4 345 346 367 366
		f 4 -643 681 682 -680
		mu 0 4 346 347 368 367
		f 4 -645 683 684 -682
		mu 0 4 347 348 369 368
		f 4 -647 685 686 -684
		mu 0 4 348 349 370 369
		f 4 -649 687 688 -686
		mu 0 4 349 350 371 370
		f 4 -651 689 690 -688
		mu 0 4 350 351 372 371
		f 4 -653 691 692 -690
		mu 0 4 351 352 373 372
		f 4 -655 693 694 -692
		mu 0 4 352 353 374 373
		f 4 -657 695 696 -694
		mu 0 4 353 354 375 374
		f 4 -659 697 698 -696
		mu 0 4 354 355 376 375
		f 4 -660 -663 699 -698
		mu 0 4 355 356 377 376
		f 4 -662 700 701 702
		mu 0 4 358 357 378 379
		f 4 -665 703 704 -701
		mu 0 4 357 359 380 378
		f 4 -667 705 706 -704
		mu 0 4 359 360 381 380
		f 4 -669 707 708 -706
		mu 0 4 360 361 382 381
		f 4 -671 709 710 -708
		mu 0 4 361 362 383 382
		f 4 -673 711 712 -710
		mu 0 4 362 363 384 383
		f 4 -675 713 714 -712
		mu 0 4 363 364 385 384
		f 4 -677 715 716 -714
		mu 0 4 364 365 386 385
		f 4 -679 717 718 -716
		mu 0 4 365 366 387 386
		f 4 -681 719 720 -718
		mu 0 4 366 367 388 387
		f 4 -683 721 722 -720
		mu 0 4 367 368 389 388
		f 4 -685 723 724 -722
		mu 0 4 368 369 390 389
		f 4 -687 725 726 -724
		mu 0 4 369 370 391 390
		f 4 -689 727 728 -726
		mu 0 4 370 371 392 391
		f 4 -691 729 730 -728
		mu 0 4 371 372 393 392
		f 4 -693 731 732 -730
		mu 0 4 372 373 394 393
		f 4 -695 733 734 -732
		mu 0 4 373 374 395 394
		f 4 -697 735 736 -734
		mu 0 4 374 375 396 395
		f 4 -699 737 738 -736
		mu 0 4 375 376 397 396
		f 4 -700 -703 739 -738
		mu 0 4 376 377 398 397
		f 3 -1 740 741
		mu 0 3 1 0 399
		f 3 -5 -742 742
		mu 0 3 4 1 400
		f 3 -8 -743 743
		mu 0 3 6 4 401
		f 3 -11 -744 744
		mu 0 3 8 6 402
		f 3 -14 -745 745
		mu 0 3 10 8 403
		f 3 -17 -746 746
		mu 0 3 12 10 404
		f 3 -20 -747 747
		mu 0 3 14 12 405
		f 3 -23 -748 748
		mu 0 3 16 14 406
		f 3 -26 -749 749
		mu 0 3 18 16 407
		f 3 -29 -750 750
		mu 0 3 20 18 408
		f 3 -32 -751 751
		mu 0 3 22 20 409
		f 3 -35 -752 752
		mu 0 3 24 22 410
		f 3 -38 -753 753
		mu 0 3 26 24 411
		f 3 -41 -754 754
		mu 0 3 28 26 412
		f 3 -44 -755 755
		mu 0 3 30 28 413
		f 3 -47 -756 756
		mu 0 3 32 30 414
		f 3 -50 -757 757
		mu 0 3 34 32 415
		f 3 -53 -758 758
		mu 0 3 36 34 416
		f 3 -56 -759 759
		mu 0 3 38 36 417
		f 3 -59 -760 -741
		mu 0 3 40 38 418
		f 3 -702 760 761
		mu 0 3 379 378 419
		f 3 -705 762 -761
		mu 0 3 378 380 420
		f 3 -707 763 -763
		mu 0 3 380 381 421
		f 3 -709 764 -764
		mu 0 3 381 382 422
		f 3 -711 765 -765
		mu 0 3 382 383 423
		f 3 -713 766 -766
		mu 0 3 383 384 424
		f 3 -715 767 -767
		mu 0 3 384 385 425
		f 3 -717 768 -768
		mu 0 3 385 386 426
		f 3 -719 769 -769
		mu 0 3 386 387 427
		f 3 -721 770 -770
		mu 0 3 387 388 428
		f 3 -723 771 -771
		mu 0 3 388 389 429
		f 3 -725 772 -772
		mu 0 3 389 390 430
		f 3 -727 773 -773
		mu 0 3 390 391 431
		f 3 -729 774 -774
		mu 0 3 391 392 432
		f 3 -731 775 -775
		mu 0 3 392 393 433
		f 3 -733 776 -776
		mu 0 3 393 394 434
		f 3 -735 777 -777
		mu 0 3 394 395 435
		f 3 -737 778 -778
		mu 0 3 395 396 436
		f 3 -739 779 -779
		mu 0 3 396 397 437
		f 3 -740 -762 -780
		mu 0 3 397 398 438;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
createNode transform -n "geom:pCone1" -p "group1";
	rename -uid "BD8FE8F4-4C59-A297-9B5F-44A3A61D95E9";
createNode mesh -n "geom:pCone1Shape" -p "geom:pCone1";
	rename -uid "07EAF056-49E9-E8AD-AA48-5BA0F4ABDB38";
	setAttr -k off ".v";
	setAttr ".iog[0].og[0].gcl" -type "componentList" 1 "f[0:20]";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 48 ".uvst[0].uvsp[0:47]" -type "float2" 0.44172999 0.157548
		 0.45276099 0.22719599 0.44172999 0.29684299 0.40971699 0.35967299 0.35985401 0.409536
		 0.29702401 0.441549 0.227377 0.45258 0.157729 0.441549 0.094898999 0.409536 0.045037001
		 0.35967299 0.013023 0.29684299 0.001992 0.22719599 0.013023 0.157548 0.045037001
		 0.094718002 0.094898999 0.044856001 0.157729 0.012842 0.227377 0.0018110001 0.29702401
		 0.012842 0.35985401 0.044856001 0.40971699 0.094718002 0.71217799 0.0018110001 0.77500802
		 0.0018110001 0.64253002 0.45258 0.824871 0.0018110001 0.99800801 0.907341 0.93517798
		 0.907341 0.86553001 0.456572 0.86553001 0.907341 0.79588199 0.907341 0.73305202 0.907341
		 0.36223701 0.456572 0.412099 0.456572 0.544577 0.907341 0.474929 0.456572 0.544577
		 0.456572 0.61422497 0.456572 0.677055 0.456572 0.72691703 0.456572 0.091146 0.456572
		 0.15397599 0.456572 0.22362401 0.907341 0.22362401 0.456572 0.29327199 0.456572 0.35610199
		 0.456572 0.46019101 0.0018110001 0.51005298 0.0018110001 0.57288301 0.0018110001
		 0.64253002 0.0018110001;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 21 ".vt[0:20]"  -3.6151011 -0.121774 -6.67727995 -4.15370798 -0.121774 -7.73435497
		 -4.99260712 -0.121774 -8.57325363 -6.04968214 -0.121774 -9.11186123 -7.22145891 -0.121774 -9.29745197
		 -8.39323521 -0.121774 -9.11186028 -9.4503088 -0.121774 -8.57325363 -10.28920841 -0.121774 -7.73435402
		 -10.82781506 -0.121774 -6.67727995 -11.0134058 -0.121774 -5.50550413 -10.82781506 -0.121774 -4.33372784
		 -10.28920841 -0.121774 -3.27665305 -9.4503088 -0.121774 -2.43775392 -8.39323521 -0.121774 -1.89914799
		 -7.22145891 -0.121774 -1.713557 -6.049683094 -0.121774 -1.89914799 -4.99260902 -0.121774 -2.43775511
		 -4.15370989 -0.121774 -3.27665305 -3.61510301 -0.121774 -4.33372784 -3.42951202 -0.121774 -5.50550413
		 -7.22145891 7.46211815 -5.50550413;
	setAttr -s 40 ".ed[0:39]"  0 19 0 19 18 0 18 17 0 17 16 0 16 15 0 15 14 0
		 14 13 0 13 12 0 12 11 0 11 10 0 10 9 0 9 8 0 8 7 0 7 6 0 6 5 0 5 4 0 4 3 0 3 2 0
		 2 1 0 1 0 0 1 20 0 20 0 0 2 20 0 3 20 0 4 20 0 5 20 0 6 20 0 7 20 0 8 20 0 9 20 0
		 10 20 0 11 20 0 12 20 0 13 20 0 14 20 0 15 20 0 16 20 0 17 20 0 18 20 0 19 20 0;
	setAttr -s 80 ".n[0:79]" -type "float3"  1e+020 1e+020 1e+020 1e+020
		 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020
		 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020
		 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020
		 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020
		 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 0.85065103 0.44721401 -0.27639201
		 0.723607 0.44721401 -0.52573103 0 1 -1e-006 0.723607 0.44721401 -0.52573103 0.52573103
		 0.44721401 -0.723607 0 1 -1e-006 0.52573103 0.44721401 -0.723607 0.276393 0.44721401
		 -0.85065103 0 1 -1e-006 0.276393 0.44721401 -0.85065103 0 0.44721401 -0.894427 0
		 1 -1e-006 0 0.44721401 -0.894427 -0.276393 0.44721401 -0.85065103 0 1 -1e-006 -0.276393
		 0.44721401 -0.85065103 -0.52573103 0.44721401 -0.723607 0 1 -1e-006 -0.52573103 0.44721401
		 -0.723607 -0.723607 0.44721401 -0.52573103 0 1 -1e-006 -0.723607 0.44721401 -0.52573103
		 -0.85065103 0.44721401 -0.276393 0 1 -1e-006 -0.85065103 0.44721401 -0.276393 -0.894427
		 0.44721401 0 0 1 -1e-006 -0.894427 0.44721401 0 -0.85065103 0.44721401 0.276393 0
		 1 -1e-006 -0.85065103 0.44721401 0.276393 -0.723607 0.44721401 0.52573103 0 1 -1e-006
		 -0.723607 0.44721401 0.52573103 -0.52573103 0.44721401 0.723607 0 1 -1e-006 -0.52573103
		 0.44721401 0.723607 -0.276393 0.44721401 0.85065103 0 1 -1e-006 -0.276393 0.44721401
		 0.85065103 0 0.44721401 0.894427 0 1 -1e-006 0 0.44721401 0.894427 0.276393 0.44721401
		 0.85065103 0 1 -1e-006 0.276393 0.44721401 0.85065103 0.52573103 0.44721401 0.723607
		 0 1 -1e-006 0.52573103 0.44721401 0.723607 0.723607 0.44721401 0.52573103 0 1 -1e-006
		 0.723607 0.44721401 0.52573103 0.85065103 0.44721401 0.276393 0 1 -1e-006 0.85065103
		 0.44721401 0.276393 0.894427 0.44721401 1e-006 0 1 -1e-006 0.894427 0.44721401 1e-006
		 0.85065103 0.44721401 -0.27639201 0 1 -1e-006;
	setAttr -s 21 -ch 80 ".fc[0:20]" -type "polyFaces" 
		f 20 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19
		mu 0 20 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19
		f 3 -20 20 21
		mu 0 3 20 21 22
		f 3 -19 22 -21
		mu 0 3 21 23 22
		f 3 -18 23 -23
		mu 0 3 24 25 26
		f 3 -17 24 -24
		mu 0 3 25 27 26
		f 3 -16 25 -25
		mu 0 3 27 28 26
		f 3 -15 26 -26
		mu 0 3 28 29 26
		f 3 -14 27 -27
		mu 0 3 30 31 32
		f 3 -13 28 -28
		mu 0 3 31 33 32
		f 3 -12 29 -29
		mu 0 3 33 34 32
		f 3 -11 30 -30
		mu 0 3 34 35 32
		f 3 -10 31 -31
		mu 0 3 35 36 32
		f 3 -9 32 -32
		mu 0 3 36 37 32
		f 3 -8 33 -33
		mu 0 3 38 39 40
		f 3 -7 34 -34
		mu 0 3 39 41 40
		f 3 -6 35 -35
		mu 0 3 41 42 40
		f 3 -5 36 -36
		mu 0 3 42 43 40
		f 3 -4 37 -37
		mu 0 3 44 45 22
		f 3 -3 38 -38
		mu 0 3 45 46 22
		f 3 -2 39 -39
		mu 0 3 46 47 22
		f 3 -1 -22 -40
		mu 0 3 47 20 22;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
createNode transform -n "geom:pTorus1" -p "group1";
	rename -uid "521736C9-43E8-6A57-8875-9F92688A23D5";
createNode mesh -n "geom:pTorus1Shape" -p "geom:pTorus1";
	rename -uid "FA3EF3FE-4A44-AA6C-4676-72AFF03F08CA";
	setAttr -k off ".v";
	setAttr ".iog[0].og[0].gcl" -type "componentList" 1 "f[0:399]";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 441 ".uvst[0].uvsp";
	setAttr ".uvst[0].uvsp[0:249]" -type "float2" 0.050000001 1 0 1 0 0.94999999
		 0.050000001 0.94999999 0.1 1 0.1 0.94999999 0.15000001 1 0.15000001 0.94999999 0.2
		 1 0.2 0.94999999 0.25 1 0.25 0.94999999 0.30000001 1 0.30000001 0.94999999 0.34999999
		 1 0.34999999 0.94999999 0.40000001 1 0.40000001 0.94999999 0.44999999 1 0.44999999
		 0.94999999 0.5 1 0.5 0.94999999 0.55000001 1 0.55000001 0.94999999 0.60000002 1 0.60000002
		 0.94999999 0.64999998 1 0.64999998 0.94999999 0.69999999 1 0.69999999 0.94999999
		 0.75 1 0.75 0.94999999 0.80000001 1 0.80000001 0.94999999 0.85000002 1 0.85000002
		 0.94999999 0.89999998 1 0.89999998 0.94999999 0.94999999 1 0.94999999 0.94999999
		 1 1 1 0.94999999 0 0.89999998 0.050000001 0.89999998 0.1 0.89999998 0.15000001 0.89999998
		 0.2 0.89999998 0.25 0.89999998 0.30000001 0.89999998 0.34999999 0.89999998 0.40000001
		 0.89999998 0.44999999 0.89999998 0.5 0.89999998 0.55000001 0.89999998 0.60000002
		 0.89999998 0.64999998 0.89999998 0.69999999 0.89999998 0.75 0.89999998 0.80000001
		 0.89999998 0.85000002 0.89999998 0.89999998 0.89999998 0.94999999 0.89999998 1 0.89999998
		 0 0.85000002 0.050000001 0.85000002 0.1 0.85000002 0.15000001 0.85000002 0.2 0.85000002
		 0.25 0.85000002 0.30000001 0.85000002 0.34999999 0.85000002 0.40000001 0.85000002
		 0.44999999 0.85000002 0.5 0.85000002 0.55000001 0.85000002 0.60000002 0.85000002
		 0.64999998 0.85000002 0.69999999 0.85000002 0.75 0.85000002 0.80000001 0.85000002
		 0.85000002 0.85000002 0.89999998 0.85000002 0.94999999 0.85000002 1 0.85000002 0
		 0.80000001 0.050000001 0.80000001 0.1 0.80000001 0.15000001 0.80000001 0.2 0.80000001
		 0.25 0.80000001 0.30000001 0.80000001 0.34999999 0.80000001 0.40000001 0.80000001
		 0.44999999 0.80000001 0.5 0.80000001 0.55000001 0.80000001 0.60000002 0.80000001
		 0.64999998 0.80000001 0.69999999 0.80000001 0.75 0.80000001 0.80000001 0.80000001
		 0.85000002 0.80000001 0.89999998 0.80000001 0.94999999 0.80000001 1 0.80000001 0
		 0.75 0.050000001 0.75 0.1 0.75 0.15000001 0.75 0.2 0.75 0.25 0.75 0.30000001 0.75
		 0.34999999 0.75 0.40000001 0.75 0.44999999 0.75 0.5 0.75 0.55000001 0.75 0.60000002
		 0.75 0.64999998 0.75 0.69999999 0.75 0.75 0.75 0.80000001 0.75 0.85000002 0.75 0.89999998
		 0.75 0.94999999 0.75 1 0.75 0 0.69999999 0.050000001 0.69999999 0.1 0.69999999 0.15000001
		 0.69999999 0.2 0.69999999 0.25 0.69999999 0.30000001 0.69999999 0.34999999 0.69999999
		 0.40000001 0.69999999 0.44999999 0.69999999 0.5 0.69999999 0.55000001 0.69999999
		 0.60000002 0.69999999 0.64999998 0.69999999 0.69999999 0.69999999 0.75 0.69999999
		 0.80000001 0.69999999 0.85000002 0.69999999 0.89999998 0.69999999 0.94999999 0.69999999
		 1 0.69999999 0 0.64999998 0.050000001 0.64999998 0.1 0.64999998 0.15000001 0.64999998
		 0.2 0.64999998 0.25 0.64999998 0.30000001 0.64999998 0.34999999 0.64999998 0.40000001
		 0.64999998 0.44999999 0.64999998 0.5 0.64999998 0.55000001 0.64999998 0.60000002
		 0.64999998 0.64999998 0.64999998 0.69999999 0.64999998 0.75 0.64999998 0.80000001
		 0.64999998 0.85000002 0.64999998 0.89999998 0.64999998 0.94999999 0.64999998 1 0.64999998
		 0 0.60000002 0.050000001 0.60000002 0.1 0.60000002 0.15000001 0.60000002 0.2 0.60000002
		 0.25 0.60000002 0.30000001 0.60000002 0.34999999 0.60000002 0.40000001 0.60000002
		 0.44999999 0.60000002 0.5 0.60000002 0.55000001 0.60000002 0.60000002 0.60000002
		 0.64999998 0.60000002 0.69999999 0.60000002 0.75 0.60000002 0.80000001 0.60000002
		 0.85000002 0.60000002 0.89999998 0.60000002 0.94999999 0.60000002 1 0.60000002 0
		 0.55000001 0.050000001 0.55000001 0.1 0.55000001 0.15000001 0.55000001 0.2 0.55000001
		 0.25 0.55000001 0.30000001 0.55000001 0.34999999 0.55000001 0.40000001 0.55000001
		 0.44999999 0.55000001 0.5 0.55000001 0.55000001 0.55000001 0.60000002 0.55000001
		 0.64999998 0.55000001 0.69999999 0.55000001 0.75 0.55000001 0.80000001 0.55000001
		 0.85000002 0.55000001 0.89999998 0.55000001 0.94999999 0.55000001 1 0.55000001 0
		 0.5 0.050000001 0.5 0.1 0.5 0.15000001 0.5 0.2 0.5 0.25 0.5 0.30000001 0.5 0.34999999
		 0.5 0.40000001 0.5 0.44999999 0.5 0.5 0.5 0.55000001 0.5 0.60000002 0.5 0.64999998
		 0.5 0.69999999 0.5 0.75 0.5 0.80000001 0.5 0.85000002 0.5 0.89999998 0.5 0.94999999
		 0.5 1 0.5 0 0.44999999 0.050000001 0.44999999 0.1 0.44999999 0.15000001 0.44999999
		 0.2 0.44999999 0.25 0.44999999 0.30000001 0.44999999 0.34999999 0.44999999 0.40000001
		 0.44999999 0.44999999 0.44999999 0.5 0.44999999 0.55000001 0.44999999 0.60000002
		 0.44999999 0.64999998 0.44999999 0.69999999 0.44999999 0.75 0.44999999 0.80000001
		 0.44999999 0.85000002 0.44999999 0.89999998 0.44999999;
	setAttr ".uvst[0].uvsp[250:440]" 0.94999999 0.44999999 1 0.44999999 0 0.40000001
		 0.050000001 0.40000001 0.1 0.40000001 0.15000001 0.40000001 0.2 0.40000001 0.25 0.40000001
		 0.30000001 0.40000001 0.34999999 0.40000001 0.40000001 0.40000001 0.44999999 0.40000001
		 0.5 0.40000001 0.55000001 0.40000001 0.60000002 0.40000001 0.64999998 0.40000001
		 0.69999999 0.40000001 0.75 0.40000001 0.80000001 0.40000001 0.85000002 0.40000001
		 0.89999998 0.40000001 0.94999999 0.40000001 1 0.40000001 0 0.34999999 0.050000001
		 0.34999999 0.1 0.34999999 0.15000001 0.34999999 0.2 0.34999999 0.25 0.34999999 0.30000001
		 0.34999999 0.34999999 0.34999999 0.40000001 0.34999999 0.44999999 0.34999999 0.5
		 0.34999999 0.55000001 0.34999999 0.60000002 0.34999999 0.64999998 0.34999999 0.69999999
		 0.34999999 0.75 0.34999999 0.80000001 0.34999999 0.85000002 0.34999999 0.89999998
		 0.34999999 0.94999999 0.34999999 1 0.34999999 0 0.30000001 0.050000001 0.30000001
		 0.1 0.30000001 0.15000001 0.30000001 0.2 0.30000001 0.25 0.30000001 0.30000001 0.30000001
		 0.34999999 0.30000001 0.40000001 0.30000001 0.44999999 0.30000001 0.5 0.30000001
		 0.55000001 0.30000001 0.60000002 0.30000001 0.64999998 0.30000001 0.69999999 0.30000001
		 0.75 0.30000001 0.80000001 0.30000001 0.85000002 0.30000001 0.89999998 0.30000001
		 0.94999999 0.30000001 1 0.30000001 0 0.25 0.050000001 0.25 0.1 0.25 0.15000001 0.25
		 0.2 0.25 0.25 0.25 0.30000001 0.25 0.34999999 0.25 0.40000001 0.25 0.44999999 0.25
		 0.5 0.25 0.55000001 0.25 0.60000002 0.25 0.64999998 0.25 0.69999999 0.25 0.75 0.25
		 0.80000001 0.25 0.85000002 0.25 0.89999998 0.25 0.94999999 0.25 1 0.25 0 0.2 0.050000001
		 0.2 0.1 0.2 0.15000001 0.2 0.2 0.2 0.25 0.2 0.30000001 0.2 0.34999999 0.2 0.40000001
		 0.2 0.44999999 0.2 0.5 0.2 0.55000001 0.2 0.60000002 0.2 0.64999998 0.2 0.69999999
		 0.2 0.75 0.2 0.80000001 0.2 0.85000002 0.2 0.89999998 0.2 0.94999999 0.2 1 0.2 0
		 0.15000001 0.050000001 0.15000001 0.1 0.15000001 0.15000001 0.15000001 0.2 0.15000001
		 0.25 0.15000001 0.30000001 0.15000001 0.34999999 0.15000001 0.40000001 0.15000001
		 0.44999999 0.15000001 0.5 0.15000001 0.55000001 0.15000001 0.60000002 0.15000001
		 0.64999998 0.15000001 0.69999999 0.15000001 0.75 0.15000001 0.80000001 0.15000001
		 0.85000002 0.15000001 0.89999998 0.15000001 0.94999999 0.15000001 1 0.15000001 0
		 0.1 0.050000001 0.1 0.1 0.1 0.15000001 0.1 0.2 0.1 0.25 0.1 0.30000001 0.1 0.34999999
		 0.1 0.40000001 0.1 0.44999999 0.1 0.5 0.1 0.55000001 0.1 0.60000002 0.1 0.64999998
		 0.1 0.69999999 0.1 0.75 0.1 0.80000001 0.1 0.85000002 0.1 0.89999998 0.1 0.94999999
		 0.1 1 0.1 0 0.050000001 0.050000001 0.050000001 0.1 0.050000001 0.15000001 0.050000001
		 0.2 0.050000001 0.25 0.050000001 0.30000001 0.050000001 0.34999999 0.050000001 0.40000001
		 0.050000001 0.44999999 0.050000001 0.5 0.050000001 0.55000001 0.050000001 0.60000002
		 0.050000001 0.64999998 0.050000001 0.69999999 0.050000001 0.75 0.050000001 0.80000001
		 0.050000001 0.85000002 0.050000001 0.89999998 0.050000001 0.94999999 0.050000001
		 1 0.050000001 0 0 0.050000001 0 0.1 0 0.15000001 0 0.2 0 0.25 0 0.30000001 0 0.34999999
		 0 0.40000001 0 0.44999999 0 0.5 0 0.55000001 0 0.60000002 0 0.64999998 0 0.69999999
		 0 0.75 0 0.80000001 0 0.85000002 0 0.89999998 0 0.94999999 0 1 0;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 400 ".vt";
	setAttr ".vt[0:165]"  7.16176319 1.075868011 5.91048193 7.011885166 1.075868011 5.6163311
		 6.7784462 1.075868011 5.38289213 6.48429489 1.075868011 5.23301506 6.15822697 1.075868011 5.18136978
		 5.83215809 1.075868011 5.23301506 5.53800821 1.075868011 5.38289213 5.30456877 1.075868011 5.6163311
		 5.15469122 1.075868011 5.91048193 5.10304689 1.075868011 6.23654985 5.15469122 1.075868011 6.56261921
		 5.30456877 1.075868011 6.85676908 5.53800821 1.075868011 7.090208054 5.83215809 1.075868011 7.24008608
		 6.15822697 1.075868011 7.29172993 6.48429489 1.075868011 7.24008512 6.7784462 1.075868011 7.090208054
		 7.011885166 1.075868011 6.85676908 7.16176224 1.075868011 6.56261921 7.21340609 1.075868011 6.23654985
		 7.21087885 1.40193605 5.89452314 7.053666115 1.40193605 5.58597517 6.80880213 1.40193605 5.34111118
		 6.50025415 1.40193605 5.18389797 6.15822697 1.40193605 5.12972593 5.81619883 1.40193605 5.18389797
		 5.50765181 1.40193605 5.34111118 5.26278782 1.40193605 5.58597612 5.10557508 1.40193605 5.89452314
		 5.051403046 1.40193605 6.23654985 5.10557508 1.40193605 6.578578 5.26278782 1.40193605 6.88712502
		 5.50765181 1.40193605 7.131989 5.81619883 1.40193605 7.28920221 6.15822697 1.40193605 7.34337378
		 6.50025415 1.40193605 7.28920221 6.80880117 1.40193605 7.131989 7.053666115 1.40193605 6.88712502
		 7.21087885 1.40193605 6.578578 7.26504993 1.40193605 6.23654985 7.35342121 1.69608605 5.84820795
		 7.17492008 1.69608605 5.49787998 6.89689684 1.69608605 5.21985722 6.54656887 1.69608605 5.041356087
		 6.15822697 1.69608605 4.97984886 5.76988506 1.69608605 5.041356087 5.41955614 1.69608605 5.21985817
		 5.14153385 1.69608605 5.49787998 4.9630332 1.69608605 5.84820795 4.90152597 1.69608605 6.23654985
		 4.9630332 1.69608605 6.62489223 5.14153385 1.69608605 6.97522116 5.41955709 1.69608605 7.25324297
		 5.76988506 1.69608605 7.4317441 6.15822697 1.69608605 7.49325085 6.54656887 1.69608605 7.4317441
		 6.89689684 1.69608605 7.25324297 7.17491913 1.69608605 6.9752202 7.35341978 1.69608605 6.62489223
		 7.41492701 1.69608605 6.23654985 7.57543516 1.92952597 5.77607107 7.36377621 1.92952597 5.36066818
		 7.034109116 1.92952597 5.031001091 6.61870623 1.92952597 4.81934214 6.15822697 1.92952597 4.74640989
		 5.69774818 1.92952597 4.81934309 5.28234386 1.92952597 5.031001091 4.9526782 1.92952597 5.36066818
		 4.74101877 1.92952597 5.77607203 4.66808701 1.92952597 6.23654985 4.74101877 1.92952597 6.69702911
		 4.9526782 1.92952597 7.11243296 5.28234386 1.92952597 7.44209909 5.69774818 1.92952597 7.65375805
		 6.15822697 1.92952597 7.72668982 6.6187048 1.92952597 7.6537571 7.034109116 1.92952597 7.44209909
		 7.36377478 1.92952597 7.11243296 7.57543421 1.92952597 6.69702911 7.64836693 1.92952597 6.23654985
		 7.85518885 2.079402924 5.68517399 7.60174894 2.079402924 5.18776989 7.20700693 2.079402924 4.79302788
		 6.70960283 2.079402924 4.53958797 6.15822697 2.079402924 4.45225906 5.60685015 2.079402924 4.53958893
		 5.109447 2.079402924 4.79302788 4.71470499 2.079402924 5.18776989 4.46126509 2.079402924 5.68517399
		 4.37393618 2.079402924 6.23654985 4.46126509 2.079402924 6.7879262 4.71470499 2.079402924 7.28532982
		 5.109447 2.079402924 7.68007183 5.6068511 2.079402924 7.93351078 6.15822697 2.079402924 8.020840645
		 6.70960283 2.079402924 7.93351078 7.20700598 2.079402924 7.68007183 7.60174799 2.079402924 7.28532982
		 7.85518789 2.079402924 6.7879262 7.9425168 2.079402924 6.23654985 8.16529846 2.13104701 5.58441305
		 7.86554384 2.13104701 4.99611187 7.39866495 2.13104701 4.52923298 6.81036377 2.13104701 4.22947884
		 6.15822697 2.13104701 4.12619114 5.50609016 2.13104701 4.22947884 4.91778898 2.13104701 4.52923393
		 4.45091009 2.13104701 4.99611187 4.15115595 2.13104701 5.58441305 4.047867775 2.13104701 6.23654985
		 4.15115595 2.13104701 6.88868713 4.45091009 2.13104701 7.47698784 4.91778898 2.13104701 7.94386578
		 5.50609016 2.13104701 8.24362087 6.15822697 2.13104701 8.34690857 6.81036282 2.13104701 8.24362087
		 7.398664 2.13104701 7.94386578 7.86554289 2.13104701 7.47698784 8.16529655 2.13104701 6.88868713
		 8.26858521 2.13104701 6.23654985 8.4754076 2.079402924 5.48365211 8.12933922 2.079402924 4.8044529
		 7.59032393 2.079402924 4.26543808 6.91112518 2.079402924 3.91936898 6.15822697 2.079402924 3.80012202
		 5.40532923 2.079402924 3.91936898 4.72613001 2.079402924 4.26543903 4.18711519 2.079402924 4.80445385
		 3.84104609 2.079402924 5.48365307 3.7217989 2.079402924 6.23654985 3.84104609 2.079402924 6.98944807
		 4.18711519 2.079402924 7.66864586 4.72613096 2.079402924 8.20766163 5.40532923 2.079402924 8.55373001
		 6.15822697 2.079402924 8.6729784 6.91112423 2.079402924 8.55373001 7.59032297 2.079402924 8.20766068
		 8.12933826 2.079402924 7.66864586 8.47540665 2.079402924 6.98944807 8.59465408 2.079402924 6.23654985
		 8.75516224 1.92952597 5.39275503 8.36731243 1.92952597 4.63155603 7.76322079 1.92952597 4.027464867
		 7.0020217896 1.92952597 3.63961506 6.15822697 1.92952597 3.50597191 5.31443214 1.92952597 3.63961601
		 4.55323315 1.92952597 4.02746582 3.94914293 1.92952597 4.63155699 3.56129289 1.92952597 5.39275503
		 3.42764902 1.92952597 6.23654985 3.56129289 1.92952597 7.080345154 3.94914293 1.92952597 7.84154415
		 4.55323315 1.92952597 8.44563389 5.31443214 1.92952597 8.8334837 6.15822697 1.92952597 8.9671278
		 7.0020217896 1.92952597 8.8334837 7.76321983 1.92952597 8.44563389 8.36730957 1.92952597 7.84154415
		 8.75516033 1.92952597 7.080345154 8.88880444 1.92952597 6.23654985 8.97717571 1.69608605 5.32061815
		 8.5561676 1.69608605 4.49434423 7.90043306 1.69608605 3.83860898 7.074159145 1.69608605 3.41760111
		 6.15822697 1.69608605 3.27253199 5.24229479 1.69608605 3.41760206;
	setAttr ".vt[166:331]" 4.41602087 1.69608605 3.83860898 3.76028609 1.69608605 4.49434423
		 3.33927894 1.69608605 5.32061815 3.1942091 1.69608605 6.23654985 3.33927894 1.69608605 7.15248203
		 3.76028609 1.69608605 7.97875595 4.41602087 1.69608605 8.63449097 5.24229479 1.69608605 9.055498123
		 6.15822697 1.69608605 9.20056725 7.074158192 1.69608605 9.055498123 7.90043211 1.69608605 8.63449001
		 8.55616665 1.69608605 7.97875595 8.97717381 1.69608605 7.15248203 9.12224388 1.69608605 6.23654985
		 9.1197176 1.40193605 5.27430391 8.67742157 1.40193605 4.40624809 7.98852921 1.40193605 3.71735597
		 7.12047291 1.40193605 3.27505994 6.15822697 1.40193605 3.12265491 5.19598007 1.40193605 3.27505994
		 4.32792521 1.40193605 3.71735597 3.63903308 1.40193605 4.40624905 3.19673705 1.40193605 5.27430391
		 3.044332027 1.40193605 6.23654985 3.19673705 1.40193605 7.19879723 3.63903308 1.40193605 8.066851616
		 4.32792616 1.40193605 8.75574398 5.19598007 1.40193605 9.19804001 6.15822697 1.40193605 9.35044384
		 7.12047291 1.40193605 9.19804001 7.98852777 1.40193605 8.75574398 8.67741966 1.40193605 8.066850662
		 9.11971569 1.40193605 7.1987958 9.27212143 1.40193605 6.23654985 9.16883373 1.075868011 5.25834513
		 8.719203 1.075868011 4.37589312 8.018884659 1.075868011 3.67557406 7.13643217 1.075868011 3.22594309
		 6.15822697 1.075868011 3.071011066 5.18002081 1.075868011 3.22594309 4.2975688 1.075868011 3.67557502
		 3.59725189 1.075868011 4.37589312 3.14761996 1.075868011 5.25834513 2.99268794 1.075868011 6.23654985
		 3.14761996 1.075868011 7.21475601 3.59725189 1.075868011 8.097207069 4.29757023 1.075868011 8.79752541
		 5.18002176 1.075868011 9.24715614 6.15822697 1.075868011 9.40208912 7.13643217 1.075868011 9.24715614
		 8.018882751 1.075868011 8.79752541 8.71920109 1.075868011 8.097207069 9.16883278 1.075868011 7.21475506
		 9.3237648 1.075868011 6.23654985 9.1197176 0.74979901 5.27430391 8.67742157 0.74979901 4.40624809
		 7.98852921 0.74979901 3.71735597 7.12047291 0.74979901 3.27505994 6.15822697 0.74979901 3.12265491
		 5.19598007 0.74979901 3.27505994 4.32792521 0.74979901 3.71735597 3.63903308 0.74979901 4.40624905
		 3.19673705 0.74979901 5.27430391 3.044332027 0.74979901 6.23654985 3.19673705 0.74979901 7.19879723
		 3.63903308 0.74979901 8.066851616 4.32792616 0.74979901 8.75574398 5.19598007 0.74979901 9.19804001
		 6.15822697 0.74979901 9.35044384 7.12047291 0.74979901 9.19804001 7.98852777 0.74979901 8.75574398
		 8.67741966 0.74979901 8.066850662 9.11971569 0.74979901 7.1987958 9.27212143 0.74979901 6.23654985
		 8.97717571 0.45564899 5.32061815 8.5561676 0.45564899 4.49434423 7.90043306 0.45564899 3.83860898
		 7.074159145 0.45564899 3.41760111 6.15822697 0.45564899 3.27253199 5.24229479 0.45564899 3.41760206
		 4.41602087 0.45564899 3.83860898 3.76028609 0.45564899 4.49434423 3.33927894 0.45564899 5.32061815
		 3.1942091 0.45564899 6.23654985 3.33927894 0.45564899 7.15248203 3.76028609 0.45564899 7.97875595
		 4.41602087 0.45564899 8.63449097 5.24229479 0.45564899 9.055498123 6.15822697 0.45564899 9.20056725
		 7.074158192 0.45564899 9.055498123 7.90043211 0.45564899 8.63449001 8.55616665 0.45564899 7.97875595
		 8.97717381 0.45564899 7.15248203 9.12224388 0.45564899 6.23654985 8.75516224 0.22220901 5.39275503
		 8.36731243 0.22220901 4.63155603 7.76322079 0.22220901 4.027464867 7.0020217896 0.22220901 3.63961506
		 6.15822697 0.22220901 3.50597095 5.31443119 0.22220901 3.63961506 4.55323315 0.22220901 4.02746582
		 3.94914198 0.22220901 4.63155603 3.56129193 0.22220901 5.39275503 3.42764807 0.22220901 6.23654985
		 3.56129193 0.22220901 7.080345154 3.94914293 0.22220901 7.84154415 4.55323315 0.22220901 8.44563389
		 5.31443214 0.22220901 8.8334837 6.15822697 0.22220901 8.9671278 7.0020217896 0.22220901 8.8334837
		 7.76321983 0.22220901 8.44563389 8.36730957 0.22220901 7.84154415 8.75516129 0.22220901 7.080345154
		 8.88880444 0.22220901 6.23654985 8.4754076 0.072332002 5.48365211 8.12933922 0.072332002 4.8044529
		 7.59032393 0.072332002 4.26543808 6.91112518 0.072332002 3.91936898 6.15822697 0.072332002 3.80012202
		 5.40532923 0.072332002 3.91936898 4.72613001 0.072332002 4.26543903 4.18711519 0.072332002 4.80445385
		 3.84104609 0.072332002 5.48365307 3.7217989 0.072332002 6.23654985 3.84104609 0.072332002 6.98944807
		 4.18711519 0.072332002 7.66864586 4.72613096 0.072332002 8.20766163 5.40532923 0.072332002 8.55373001
		 6.15822697 0.072332002 8.6729784 6.91112423 0.072332002 8.55373001 7.59032297 0.072332002 8.20766068
		 8.12933826 0.072332002 7.66864586 8.47540665 0.072332002 6.98944807 8.59465408 0.072332002 6.23654985
		 8.16529846 0.020687999 5.58441305 7.86554384 0.020687999 4.99611187 7.39866495 0.020687999 4.52923298
		 6.81036377 0.020687999 4.22947884 6.15822697 0.020687999 4.12619114 5.50609016 0.020687999 4.22947884
		 4.91778898 0.020687999 4.52923393 4.45091009 0.020687999 4.99611187 4.15115595 0.020687999 5.58441305
		 4.047867775 0.020687999 6.23654985 4.15115595 0.020687999 6.88868713 4.45091009 0.020687999 7.47698784
		 4.91778898 0.020687999 7.94386578 5.50609016 0.020687999 8.24362087 6.15822697 0.020687999 8.34690857
		 6.81036282 0.020687999 8.24362087 7.398664 0.020687999 7.94386578 7.86554289 0.020687999 7.47698784
		 8.16529655 0.020687999 6.88868713 8.26858521 0.020687999 6.23654985 7.85518885 0.072332002 5.68517399
		 7.60174894 0.072332002 5.18776989 7.20700693 0.072332002 4.79302788 6.70960283 0.072332002 4.53958893
		 6.15822697 0.072332002 4.45225906 5.6068511 0.072332002 4.53958893 5.109447 0.072332002 4.79302883
		 4.71470499 0.072332002 5.18777084 4.46126604 0.072332002 5.68517399 4.37393618 0.072332002 6.23654985
		 4.46126604 0.072332002 6.7879262 4.71470594 0.072332002 7.28532982;
	setAttr ".vt[332:399]" 5.109447 0.072332002 7.68007088 5.6068511 0.072332002 7.93351078
		 6.15822697 0.072332002 8.020840645 6.70960283 0.072332002 7.93351078 7.20700598 0.072332002 7.68007088
		 7.60174799 0.072332002 7.28532982 7.85518694 0.072332002 6.7879262 7.9425168 0.072332002 6.23654985
		 7.57543516 0.22220901 5.77607203 7.36377621 0.22220901 5.36066818 7.034109116 0.22220901 5.031001091
		 6.6187048 0.22220901 4.81934309 6.15822697 0.22220901 4.74640989 5.69774818 0.22220901 4.81934309
		 5.28234386 0.22220901 5.031002045 4.9526782 0.22220901 5.36066818 4.7410202 0.22220901 5.77607203
		 4.66808701 0.22220901 6.23654985 4.7410202 0.22220901 6.69702911 4.9526782 0.22220901 7.112432
		 5.28234482 0.22220901 7.44209909 5.69774818 0.22220901 7.6537571 6.15822697 0.22220901 7.72668982
		 6.6187048 0.22220901 7.6537571 7.034109116 0.22220901 7.44209814 7.36377478 0.22220901 7.112432
		 7.57543421 0.22220901 6.69702911 7.64836597 0.22220901 6.23654985 7.35341978 0.45564801 5.84820795
		 7.17491913 0.45564801 5.49787998 6.89689684 0.45564801 5.21985817 6.54656887 0.45564801 5.04135704
		 6.15822697 0.45564801 4.97984982 5.76988506 0.45564801 5.04135704 5.41955709 0.45564801 5.21985817
		 5.14153481 0.45564801 5.49787998 4.96303415 0.45564801 5.84820795 4.90152693 0.45564801 6.23654985
		 4.96303415 0.45564801 6.62489223 5.14153481 0.45564801 6.9752202 5.41955709 0.45564801 7.25324202
		 5.76988506 0.45564801 7.43174314 6.15822697 0.45564801 7.49324989 6.54656792 0.45564801 7.43174314
		 6.89689684 0.45564801 7.25324202 7.17491817 0.45564801 6.9752202 7.35341978 0.45564801 6.62489223
		 7.41492701 0.45564801 6.23654985 7.2108779 0.74979901 5.89452314 7.053666115 0.74979901 5.58597612
		 6.80880117 0.74979901 5.34111118 6.50025415 0.74979901 5.18389893 6.15822697 0.74979901 5.12972689
		 5.81619978 0.74979901 5.18389893 5.50765181 0.74979901 5.34111118 5.26278782 0.74979901 5.58597612
		 5.10557604 0.74979901 5.89452314 5.051403999 0.74979901 6.23654985 5.10557604 0.74979901 6.57857704
		 5.26278782 0.74979901 6.88712406 5.50765324 0.74979901 7.131989 5.81619978 0.74979901 7.28920078
		 6.15822697 0.74979901 7.34337282 6.50025415 0.74979901 7.28920078 6.80880117 0.74979901 7.131989
		 7.053665161 0.74979901 6.88712406 7.2108779 0.74979901 6.57857704 7.26504993 0.74979901 6.23654985;
	setAttr -s 800 ".ed";
	setAttr ".ed[0:165]"  1 0 0 0 20 0 20 21 0 21 1 0 2 1 0 21 22 0 22 2 0 3 2 0
		 22 23 0 23 3 0 4 3 0 23 24 0 24 4 0 5 4 0 24 25 0 25 5 0 6 5 0 25 26 0 26 6 0 7 6 0
		 26 27 0 27 7 0 8 7 0 27 28 0 28 8 0 9 8 0 28 29 0 29 9 0 10 9 0 29 30 0 30 10 0 11 10 0
		 30 31 0 31 11 0 12 11 0 31 32 0 32 12 0 13 12 0 32 33 0 33 13 0 14 13 0 33 34 0 34 14 0
		 15 14 0 34 35 0 35 15 0 16 15 0 35 36 0 36 16 0 17 16 0 36 37 0 37 17 0 18 17 0 37 38 0
		 38 18 0 19 18 0 38 39 0 39 19 0 0 19 0 39 20 0 20 40 0 40 41 0 41 21 0 41 42 0 42 22 0
		 42 43 0 43 23 0 43 44 0 44 24 0 44 45 0 45 25 0 45 46 0 46 26 0 46 47 0 47 27 0 47 48 0
		 48 28 0 48 49 0 49 29 0 49 50 0 50 30 0 50 51 0 51 31 0 51 52 0 52 32 0 52 53 0 53 33 0
		 53 54 0 54 34 0 54 55 0 55 35 0 55 56 0 56 36 0 56 57 0 57 37 0 57 58 0 58 38 0 58 59 0
		 59 39 0 59 40 0 40 60 0 60 61 0 61 41 0 61 62 0 62 42 0 62 63 0 63 43 0 63 64 0 64 44 0
		 64 65 0 65 45 0 65 66 0 66 46 0 66 67 0 67 47 0 67 68 0 68 48 0 68 69 0 69 49 0 69 70 0
		 70 50 0 70 71 0 71 51 0 71 72 0 72 52 0 72 73 0 73 53 0 73 74 0 74 54 0 74 75 0 75 55 0
		 75 76 0 76 56 0 76 77 0 77 57 0 77 78 0 78 58 0 78 79 0 79 59 0 79 60 0 60 80 0 80 81 0
		 81 61 0 81 82 0 82 62 0 82 83 0 83 63 0 83 84 0 84 64 0 84 85 0 85 65 0 85 86 0 86 66 0
		 86 87 0 87 67 0 87 88 0 88 68 0 88 89 0 89 69 0 89 90 0 90 70 0 90 91 0 91 71 0 91 92 0
		 92 72 0 92 93 0;
	setAttr ".ed[166:331]" 93 73 0 93 94 0 94 74 0 94 95 0 95 75 0 95 96 0 96 76 0
		 96 97 0 97 77 0 97 98 0 98 78 0 98 99 0 99 79 0 99 80 0 80 100 0 100 101 0 101 81 0
		 101 102 0 102 82 0 102 103 0 103 83 0 103 104 0 104 84 0 104 105 0 105 85 0 105 106 0
		 106 86 0 106 107 0 107 87 0 107 108 0 108 88 0 108 109 0 109 89 0 109 110 0 110 90 0
		 110 111 0 111 91 0 111 112 0 112 92 0 112 113 0 113 93 0 113 114 0 114 94 0 114 115 0
		 115 95 0 115 116 0 116 96 0 116 117 0 117 97 0 117 118 0 118 98 0 118 119 0 119 99 0
		 119 100 0 100 120 0 120 121 0 121 101 0 121 122 0 122 102 0 122 123 0 123 103 0 123 124 0
		 124 104 0 124 125 0 125 105 0 125 126 0 126 106 0 126 127 0 127 107 0 127 128 0 128 108 0
		 128 129 0 129 109 0 129 130 0 130 110 0 130 131 0 131 111 0 131 132 0 132 112 0 132 133 0
		 133 113 0 133 134 0 134 114 0 134 135 0 135 115 0 135 136 0 136 116 0 136 137 0 137 117 0
		 137 138 0 138 118 0 138 139 0 139 119 0 139 120 0 120 140 0 140 141 0 141 121 0 141 142 0
		 142 122 0 142 143 0 143 123 0 143 144 0 144 124 0 144 145 0 145 125 0 145 146 0 146 126 0
		 146 147 0 147 127 0 147 148 0 148 128 0 148 149 0 149 129 0 149 150 0 150 130 0 150 151 0
		 151 131 0 151 152 0 152 132 0 152 153 0 153 133 0 153 154 0 154 134 0 154 155 0 155 135 0
		 155 156 0 156 136 0 156 157 0 157 137 0 157 158 0 158 138 0 158 159 0 159 139 0 159 140 0
		 140 160 0 160 161 0 161 141 0 161 162 0 162 142 0 162 163 0 163 143 0 163 164 0 164 144 0
		 164 165 0 165 145 0 165 166 0 166 146 0 166 167 0 167 147 0 167 168 0 168 148 0 168 169 0
		 169 149 0 169 170 0 170 150 0 170 171 0 171 151 0 171 172 0 172 152 0 172 173 0 173 153 0
		 173 174 0 174 154 0 174 175 0 175 155 0 175 176 0;
	setAttr ".ed[332:497]" 176 156 0 176 177 0 177 157 0 177 178 0 178 158 0 178 179 0
		 179 159 0 179 160 0 160 180 0 180 181 0 181 161 0 181 182 0 182 162 0 182 183 0 183 163 0
		 183 184 0 184 164 0 184 185 0 185 165 0 185 186 0 186 166 0 186 187 0 187 167 0 187 188 0
		 188 168 0 188 189 0 189 169 0 189 190 0 190 170 0 190 191 0 191 171 0 191 192 0 192 172 0
		 192 193 0 193 173 0 193 194 0 194 174 0 194 195 0 195 175 0 195 196 0 196 176 0 196 197 0
		 197 177 0 197 198 0 198 178 0 198 199 0 199 179 0 199 180 0 180 200 0 200 201 0 201 181 0
		 201 202 0 202 182 0 202 203 0 203 183 0 203 204 0 204 184 0 204 205 0 205 185 0 205 206 0
		 206 186 0 206 207 0 207 187 0 207 208 0 208 188 0 208 209 0 209 189 0 209 210 0 210 190 0
		 210 211 0 211 191 0 211 212 0 212 192 0 212 213 0 213 193 0 213 214 0 214 194 0 214 215 0
		 215 195 0 215 216 0 216 196 0 216 217 0 217 197 0 217 218 0 218 198 0 218 219 0 219 199 0
		 219 200 0 200 220 0 220 221 0 221 201 0 221 222 0 222 202 0 222 223 0 223 203 0 223 224 0
		 224 204 0 224 225 0 225 205 0 225 226 0 226 206 0 226 227 0 227 207 0 227 228 0 228 208 0
		 228 229 0 229 209 0 229 230 0 230 210 0 230 231 0 231 211 0 231 232 0 232 212 0 232 233 0
		 233 213 0 233 234 0 234 214 0 234 235 0 235 215 0 235 236 0 236 216 0 236 237 0 237 217 0
		 237 238 0 238 218 0 238 239 0 239 219 0 239 220 0 220 240 0 240 241 0 241 221 0 241 242 0
		 242 222 0 242 243 0 243 223 0 243 244 0 244 224 0 244 245 0 245 225 0 245 246 0 246 226 0
		 246 247 0 247 227 0 247 248 0 248 228 0 248 249 0 249 229 0 249 250 0 250 230 0 250 251 0
		 251 231 0 251 252 0 252 232 0 252 253 0 253 233 0 253 254 0 254 234 0 254 255 0 255 235 0
		 255 256 0 256 236 0 256 257 0 257 237 0 257 258 0 258 238 0 258 259 0;
	setAttr ".ed[498:663]" 259 239 0 259 240 0 240 260 0 260 261 0 261 241 0 261 262 0
		 262 242 0 262 263 0 263 243 0 263 264 0 264 244 0 264 265 0 265 245 0 265 266 0 266 246 0
		 266 267 0 267 247 0 267 268 0 268 248 0 268 269 0 269 249 0 269 270 0 270 250 0 270 271 0
		 271 251 0 271 272 0 272 252 0 272 273 0 273 253 0 273 274 0 274 254 0 274 275 0 275 255 0
		 275 276 0 276 256 0 276 277 0 277 257 0 277 278 0 278 258 0 278 279 0 279 259 0 279 260 0
		 260 280 0 280 281 0 281 261 0 281 282 0 282 262 0 282 283 0 283 263 0 283 284 0 284 264 0
		 284 285 0 285 265 0 285 286 0 286 266 0 286 287 0 287 267 0 287 288 0 288 268 0 288 289 0
		 289 269 0 289 290 0 290 270 0 290 291 0 291 271 0 291 292 0 292 272 0 292 293 0 293 273 0
		 293 294 0 294 274 0 294 295 0 295 275 0 295 296 0 296 276 0 296 297 0 297 277 0 297 298 0
		 298 278 0 298 299 0 299 279 0 299 280 0 280 300 0 300 301 0 301 281 0 301 302 0 302 282 0
		 302 303 0 303 283 0 303 304 0 304 284 0 304 305 0 305 285 0 305 306 0 306 286 0 306 307 0
		 307 287 0 307 308 0 308 288 0 308 309 0 309 289 0 309 310 0 310 290 0 310 311 0 311 291 0
		 311 312 0 312 292 0 312 313 0 313 293 0 313 314 0 314 294 0 314 315 0 315 295 0 315 316 0
		 316 296 0 316 317 0 317 297 0 317 318 0 318 298 0 318 319 0 319 299 0 319 300 0 300 320 0
		 320 321 0 321 301 0 321 322 0 322 302 0 322 323 0 323 303 0 323 324 0 324 304 0 324 325 0
		 325 305 0 325 326 0 326 306 0 326 327 0 327 307 0 327 328 0 328 308 0 328 329 0 329 309 0
		 329 330 0 330 310 0 330 331 0 331 311 0 331 332 0 332 312 0 332 333 0 333 313 0 333 334 0
		 334 314 0 334 335 0 335 315 0 335 336 0 336 316 0 336 337 0 337 317 0 337 338 0 338 318 0
		 338 339 0 339 319 0 339 320 0 320 340 0 340 341 0 341 321 0 341 342 0;
	setAttr ".ed[664:799]" 342 322 0 342 343 0 343 323 0 343 344 0 344 324 0 344 345 0
		 345 325 0 345 346 0 346 326 0 346 347 0 347 327 0 347 348 0 348 328 0 348 349 0 349 329 0
		 349 350 0 350 330 0 350 351 0 351 331 0 351 352 0 352 332 0 352 353 0 353 333 0 353 354 0
		 354 334 0 354 355 0 355 335 0 355 356 0 356 336 0 356 357 0 357 337 0 357 358 0 358 338 0
		 358 359 0 359 339 0 359 340 0 340 360 0 360 361 0 361 341 0 361 362 0 362 342 0 362 363 0
		 363 343 0 363 364 0 364 344 0 364 365 0 365 345 0 365 366 0 366 346 0 366 367 0 367 347 0
		 367 368 0 368 348 0 368 369 0 369 349 0 369 370 0 370 350 0 370 371 0 371 351 0 371 372 0
		 372 352 0 372 373 0 373 353 0 373 374 0 374 354 0 374 375 0 375 355 0 375 376 0 376 356 0
		 376 377 0 377 357 0 377 378 0 378 358 0 378 379 0 379 359 0 379 360 0 360 380 0 380 381 0
		 381 361 0 381 382 0 382 362 0 382 383 0 383 363 0 383 384 0 384 364 0 384 385 0 385 365 0
		 385 386 0 386 366 0 386 387 0 387 367 0 387 388 0 388 368 0 388 389 0 389 369 0 389 390 0
		 390 370 0 390 391 0 391 371 0 391 392 0 392 372 0 392 393 0 393 373 0 393 394 0 394 374 0
		 394 395 0 395 375 0 395 396 0 396 376 0 396 397 0 397 377 0 397 398 0 398 378 0 398 399 0
		 399 379 0 399 380 0 380 0 0 1 381 0 2 382 0 3 383 0 4 384 0 5 385 0 6 386 0 7 387 0
		 8 388 0 9 389 0 10 390 0 11 391 0 12 392 0 13 393 0 14 394 0 15 395 0 16 396 0 17 397 0
		 18 398 0 19 399 0;
	setAttr -s 1600 ".n";
	setAttr ".n[0:165]" -type "float3"  1e+020 1e+020 1e+020 1e+020 1e+020 1e+020
		 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 -0.58778501 1e-006 0.809017 -0.809017 1e-006
		 0.58778501 -0.76642197 0.32020199 0.55683798 -0.55683798 0.32020199 0.76642197 -0.309017
		 1e-006 0.95105702 -0.58778501 1e-006 0.809017 -0.55683798 0.32020199 0.76642197 -0.29274699
		 0.32020199 0.90098298 0 1e-006 1 -0.309017 1e-006 0.95105702 -0.29274699 0.32020199
		 0.90098298 0 0.32020199 0.94734901 0.309017 1e-006 0.951056 0 1e-006 1 0 0.32020199
		 0.94734901 0.29274699 0.32020199 0.90098298 0.58778501 1e-006 0.809017 0.309017 1e-006
		 0.951056 0.29274699 0.32020199 0.90098298 0.55683798 0.32020199 0.76642102 0.809017
		 1e-006 0.58778501 0.58778501 1e-006 0.809017 0.55683798 0.32020199 0.76642102 0.76642197
		 0.32020199 0.55683798 0.95105702 1e-006 0.309017 0.809017 1e-006 0.58778501 0.76642197
		 0.32020199 0.55683798 0.90098298 0.32020199 0.29274699 1 1e-006 0 0.95105702 1e-006
		 0.309017 0.90098298 0.32020199 0.29274699 0.94734901 0.32020199 0 0.951056 1e-006
		 -0.309017 1 1e-006 0 0.94734901 0.32020199 0 0.90098298 0.32020199 -0.29274699 0.809017
		 1e-006 -0.58778501 0.951056 1e-006 -0.309017 0.90098298 0.32020199 -0.29274699 0.76642197
		 0.32020199 -0.55683798 0.58778501 1e-006 -0.809017 0.809017 1e-006 -0.58778501 0.76642197
		 0.32020199 -0.55683798 0.55683798 0.32020199 -0.76642197 0.309017 1e-006 -0.95105702
		 0.58778501 1e-006 -0.809017 0.55683798 0.32020199 -0.76642197 0.29274699 0.32020199
		 -0.90098298 0 1e-006 -1 0.309017 1e-006 -0.95105702 0.29274699 0.32020199 -0.90098298
		 0 0.32020199 -0.94734901 -0.309017 1e-006 -0.951056 0 1e-006 -1 0 0.32020199 -0.94734901
		 -0.29274699 0.32020199 -0.90098298 -0.58778501 1e-006 -0.809017 -0.309017 1e-006
		 -0.951056 -0.29274699 0.32020199 -0.90098298 -0.55683798 0.32020199 -0.76642197 -0.809017
		 1e-006 -0.58778501 -0.58778501 1e-006 -0.809017 -0.55683798 0.32020199 -0.76642197
		 -0.76642197 0.32020199 -0.55683798 -0.95105702 1e-006 -0.309017 -0.809017 1e-006
		 -0.58778501 -0.76642197 0.32020199 -0.55683798 -0.90098298 0.32020199 -0.29274699
		 -1 1e-006 -1e-006 -0.95105702 1e-006 -0.309017 -0.90098298 0.32020199 -0.29274699
		 -0.94734901 0.32020199 -1e-006 -0.95105702 1e-006 0.30901599 -1 1e-006 -1e-006 -0.94734901
		 0.32020199 -1e-006 -0.90098298 0.32020199 0.29274601 -0.76642197 0.32020199 0.55683798
		 -0.90098298 0.32020199 0.29274601 -0.75760198 0.60452002 0.246159 -0.64445502 0.60452002
		 0.46822399 -0.55683798 0.32020199 0.76642197 -0.76642197 0.32020199 0.55683798 -0.64445502
		 0.60452002 0.46822399 -0.46822399 0.60452002 0.64445502 -0.29274699 0.32020199 0.90098298
		 -0.55683798 0.32020199 0.76642197 -0.46822399 0.60452002 0.64445502 -0.24616 0.60452002
		 0.75760198 0 0.32020199 0.94734901 -0.29274699 0.32020199 0.90098298 -0.24616 0.60452002
		 0.75760198 0 0.60452002 0.79658997 0.29274699 0.32020199 0.90098298 0 0.32020199
		 0.94734901 0 0.60452002 0.79658997 0.24616 0.60452002 0.75760198 0.55683798 0.32020199
		 0.76642102 0.29274699 0.32020199 0.90098298 0.24616 0.60452002 0.75760198 0.46822399
		 0.60452002 0.64445502 0.76642197 0.32020199 0.55683798 0.55683798 0.32020199 0.76642102
		 0.46822399 0.60452002 0.64445502 0.64445502 0.60452002 0.46822399 0.90098298 0.32020199
		 0.29274699 0.76642197 0.32020199 0.55683798 0.64445502 0.60452002 0.46822399 0.75760198
		 0.60452002 0.24616 0.94734901 0.32020199 0 0.90098298 0.32020199 0.29274699 0.75760198
		 0.60452002 0.24616 0.79658997 0.60452002 0 0.90098298 0.32020199 -0.29274699 0.94734901
		 0.32020199 0 0.79658997 0.60452002 0 0.75760198 0.60452002 -0.24616 0.76642197 0.32020199
		 -0.55683798 0.90098298 0.32020199 -0.29274699 0.75760198 0.60452002 -0.24616 0.64445502
		 0.60452002 -0.46822399 0.55683798 0.32020199 -0.76642197 0.76642197 0.32020199 -0.55683798
		 0.64445502 0.60452002 -0.46822399 0.46822399 0.60452002 -0.64445502 0.29274699 0.32020199
		 -0.90098298 0.55683798 0.32020199 -0.76642197 0.46822399 0.60452002 -0.64445502 0.24616
		 0.60452002 -0.75760198 0 0.32020199 -0.94734901 0.29274699 0.32020199 -0.90098298
		 0.24616 0.60452002 -0.75760198 0 0.60452002 -0.79658997 -0.29274699 0.32020199 -0.90098298
		 0 0.32020199 -0.94734901 0 0.60452002 -0.79658997 -0.24616 0.60452002 -0.75760198
		 -0.55683798 0.32020199 -0.76642197 -0.29274699 0.32020199 -0.90098298 -0.24616 0.60452002
		 -0.75760198 -0.46822399 0.60452002 -0.64445502 -0.76642197 0.32020199 -0.55683798
		 -0.55683798 0.32020199 -0.76642197 -0.46822399 0.60452002 -0.64445502 -0.64445502
		 0.60452002 -0.46822399 -0.90098298 0.32020199 -0.29274699 -0.76642197 0.32020199
		 -0.55683798 -0.64445502 0.60452002 -0.46822399 -0.75760198 0.60452002 -0.24616 -0.94734901
		 0.32020199 -1e-006 -0.90098298 0.32020199 -0.29274699 -0.75760198 0.60452002 -0.24616
		 -0.79658997 0.60452002 -1e-006 -0.90098298 0.32020199 0.29274601 -0.94734901 0.32020199
		 -1e-006 -0.79658997 0.60452002 -1e-006 -0.75760198 0.60452002 0.246159 -0.64445502
		 0.60452002 0.46822399 -0.75760198 0.60452002 0.246159 -0.53865802 0.82414502 0.17501999
		 -0.45820999 0.82414502 0.33290899 -0.46822399 0.60452002 0.64445502 -0.64445502 0.60452002
		 0.46822399;
	setAttr ".n[166:331]" -type "float3"  -0.45820999 0.82414502 0.33290899 -0.33290899
		 0.82414502 0.45820999 -0.24616 0.60452002 0.75760198 -0.46822399 0.60452002 0.64445502
		 -0.33290899 0.82414502 0.45820999 -0.17502099 0.82414502 0.53865802 0 0.60452002
		 0.79658997 -0.24616 0.60452002 0.75760198 -0.17502099 0.82414502 0.53865802 0 0.82414502
		 0.56637901 0.24616 0.60452002 0.75760198 0 0.60452002 0.79658997 0 0.82414502 0.56637901
		 0.17502099 0.82414502 0.53865802 0.46822399 0.60452002 0.64445502 0.24616 0.60452002
		 0.75760198 0.17502099 0.82414502 0.53865802 0.33290899 0.82414502 0.45820999 0.64445502
		 0.60452002 0.46822399 0.46822399 0.60452002 0.64445502 0.33290899 0.82414502 0.45820999
		 0.45820999 0.82414502 0.33290899 0.75760198 0.60452002 0.24616 0.64445502 0.60452002
		 0.46822399 0.45820999 0.82414502 0.33290899 0.53865802 0.82414502 0.17502099 0.79658997
		 0.60452002 0 0.75760198 0.60452002 0.24616 0.53865802 0.82414502 0.17502099 0.56637901
		 0.82414502 0 0.75760198 0.60452002 -0.24616 0.79658997 0.60452002 0 0.56637901 0.82414502
		 0 0.53865802 0.82414502 -0.17502099 0.64445502 0.60452002 -0.46822399 0.75760198
		 0.60452002 -0.24616 0.53865802 0.82414502 -0.17502099 0.45820999 0.82414502 -0.33290899
		 0.46822399 0.60452002 -0.64445502 0.64445502 0.60452002 -0.46822399 0.45820999 0.82414502
		 -0.33290899 0.33290899 0.82414502 -0.45820999 0.24616 0.60452002 -0.75760198 0.46822399
		 0.60452002 -0.64445502 0.33290899 0.82414502 -0.45820999 0.17502099 0.82414502 -0.53865802
		 0 0.60452002 -0.79658997 0.24616 0.60452002 -0.75760198 0.17502099 0.82414502 -0.53865802
		 0 0.82414502 -0.56637901 -0.24616 0.60452002 -0.75760198 0 0.60452002 -0.79658997
		 0 0.82414502 -0.56637901 -0.17502099 0.82414502 -0.53865898 -0.46822399 0.60452002
		 -0.64445502 -0.24616 0.60452002 -0.75760198 -0.17502099 0.82414502 -0.53865898 -0.33290899
		 0.82414502 -0.45820999 -0.64445502 0.60452002 -0.46822399 -0.46822399 0.60452002
		 -0.64445502 -0.33290899 0.82414502 -0.45820999 -0.45820999 0.82414502 -0.33290899
		 -0.75760198 0.60452002 -0.24616 -0.64445502 0.60452002 -0.46822399 -0.45820999 0.82414502
		 -0.33290899 -0.53865898 0.82414502 -0.17502099 -0.79658997 0.60452002 -1e-006 -0.75760198
		 0.60452002 -0.24616 -0.53865898 0.82414502 -0.17502099 -0.56637901 0.82414502 -1e-006
		 -0.75760198 0.60452002 0.246159 -0.79658997 0.60452002 -1e-006 -0.56637901 0.82414502
		 -1e-006 -0.53865802 0.82414502 0.17501999 -0.45820999 0.82414502 0.33290899 -0.53865802
		 0.82414502 0.17501999 -0.26821199 0.95941001 0.087146997 -0.228155 0.95941001 0.165764
		 -0.33290899 0.82414502 0.45820999 -0.45820999 0.82414502 0.33290899 -0.228155 0.95941001
		 0.165764 -0.165764 0.95941001 0.228155 -0.17502099 0.82414502 0.53865802 -0.33290899
		 0.82414502 0.45820999 -0.165764 0.95941001 0.228155 -0.087146997 0.95941001 0.268213
		 0 0.82414502 0.56637901 -0.17502099 0.82414502 0.53865802 -0.087146997 0.95941001
		 0.268213 0 0.95941001 0.282015 0.17502099 0.82414502 0.53865802 0 0.82414502 0.56637901
		 0 0.95941001 0.282015 0.087148003 0.95941001 0.26821199 0.33290899 0.82414502 0.45820999
		 0.17502099 0.82414502 0.53865802 0.087148003 0.95941001 0.26821199 0.165764 0.95941001
		 0.228155 0.45820999 0.82414502 0.33290899 0.33290899 0.82414502 0.45820999 0.165764
		 0.95941001 0.228155 0.228155 0.95941001 0.165764 0.53865802 0.82414502 0.17502099
		 0.45820999 0.82414502 0.33290899 0.228155 0.95941001 0.165764 0.268213 0.95941001
		 0.087146997 0.56637901 0.82414502 0 0.53865802 0.82414502 0.17502099 0.268213 0.95941001
		 0.087146997 0.282015 0.95941001 0 0.53865802 0.82414502 -0.17502099 0.56637901 0.82414502
		 0 0.282015 0.95941001 0 0.268213 0.95941001 -0.087148003 0.45820999 0.82414502 -0.33290899
		 0.53865802 0.82414502 -0.17502099 0.268213 0.95941001 -0.087148003 0.228155 0.95941001
		 -0.165765 0.33290899 0.82414502 -0.45820999 0.45820999 0.82414502 -0.33290899 0.228155
		 0.95941001 -0.165765 0.165764 0.95941001 -0.228155 0.17502099 0.82414502 -0.53865802
		 0.33290899 0.82414502 -0.45820999 0.165764 0.95941001 -0.228155 0.087148003 0.95941001
		 -0.268213 0 0.82414502 -0.56637901 0.17502099 0.82414502 -0.53865802 0.087148003
		 0.95941001 -0.268213 0 0.95941001 -0.282015 -0.17502099 0.82414502 -0.53865898 0
		 0.82414502 -0.56637901 0 0.95941001 -0.282015 -0.087148003 0.95941001 -0.268213 -0.33290899
		 0.82414502 -0.45820999 -0.17502099 0.82414502 -0.53865898 -0.087148003 0.95941001
		 -0.268213 -0.165765 0.95941001 -0.228155 -0.45820999 0.82414502 -0.33290899 -0.33290899
		 0.82414502 -0.45820999 -0.165765 0.95941001 -0.228155 -0.228155 0.95941001 -0.165765
		 -0.53865898 0.82414502 -0.17502099 -0.45820999 0.82414502 -0.33290899 -0.228155 0.95941001
		 -0.165765 -0.268213 0.95941001 -0.087148003 -0.56637901 0.82414502 -1e-006 -0.53865898
		 0.82414502 -0.17502099 -0.268213 0.95941001 -0.087148003 -0.28201601 0.95941001 0
		 -0.53865802 0.82414502 0.17501999 -0.56637901 0.82414502 -1e-006 -0.28201601 0.95941001
		 0 -0.26821199 0.95941001 0.087146997 -0.228155 0.95941001 0.165764 -0.26821199 0.95941001
		 0.087146997 0.026302001 0.99961698 -0.0085460003 0.022374 0.99961698 -0.016256001
		 -0.165764 0.95941001 0.228155 -0.228155 0.95941001 0.165764 0.022374 0.99961698 -0.016256001
		 0.016256001 0.99961698 -0.022374 -0.087146997 0.95941001 0.268213 -0.165764 0.95941001
		 0.228155 0.016256001 0.99961698 -0.022374 0.0085460003 0.99961698 -0.026302001;
	setAttr ".n[332:497]" -type "float3"  0 0.95941001 0.282015 -0.087146997 0.95941001
		 0.268213 0.0085460003 0.99961698 -0.026302001 0 0.99961698 -0.027656 0.087148003
		 0.95941001 0.26821199 0 0.95941001 0.282015 0 0.99961698 -0.027656 -0.0085460003
		 0.99961698 -0.026302001 0.165764 0.95941001 0.228155 0.087148003 0.95941001 0.26821199
		 -0.0085460003 0.99961698 -0.026302001 -0.016256001 0.99961698 -0.022374 0.228155
		 0.95941001 0.165764 0.165764 0.95941001 0.228155 -0.016256001 0.99961698 -0.022374
		 -0.022374 0.99961698 -0.016256001 0.268213 0.95941001 0.087146997 0.228155 0.95941001
		 0.165764 -0.022374 0.99961698 -0.016256001 -0.026302001 0.99961698 -0.0085460003
		 0.282015 0.95941001 0 0.268213 0.95941001 0.087146997 -0.026302001 0.99961698 -0.0085460003
		 -0.027656 0.99961698 0 0.268213 0.95941001 -0.087148003 0.282015 0.95941001 0 -0.027656
		 0.99961698 0 -0.026302001 0.99961698 0.0085460003 0.228155 0.95941001 -0.165765 0.268213
		 0.95941001 -0.087148003 -0.026302001 0.99961698 0.0085460003 -0.022374 0.99961698
		 0.016256001 0.165764 0.95941001 -0.228155 0.228155 0.95941001 -0.165765 -0.022374
		 0.99961698 0.016256001 -0.016256001 0.99961698 0.022374 0.087148003 0.95941001 -0.268213
		 0.165764 0.95941001 -0.228155 -0.016256001 0.99961698 0.022374 -0.0085460003 0.99961698
		 0.026302001 0 0.95941001 -0.282015 0.087148003 0.95941001 -0.268213 -0.0085460003
		 0.99961698 0.026302001 0 0.99961698 0.027656 -0.087148003 0.95941001 -0.268213 0
		 0.95941001 -0.282015 0 0.99961698 0.027656 0.0085460003 0.99961698 0.026302001 -0.165765
		 0.95941001 -0.228155 -0.087148003 0.95941001 -0.268213 0.0085460003 0.99961698 0.026302001
		 0.016256001 0.99961698 0.022374 -0.228155 0.95941001 -0.165765 -0.165765 0.95941001
		 -0.228155 0.016256001 0.99961698 0.022374 0.022374 0.99961698 0.016256001 -0.268213
		 0.95941001 -0.087148003 -0.228155 0.95941001 -0.165765 0.022374 0.99961698 0.016256001
		 0.026302001 0.99961698 0.0085460003 -0.28201601 0.95941001 0 -0.268213 0.95941001
		 -0.087148003 0.026302001 0.99961698 0.0085460003 0.027656 0.99961698 0 -0.26821199
		 0.95941001 0.087146997 -0.28201601 0.95941001 0 0.027656 0.99961698 0 0.026302001
		 0.99961698 -0.0085460003 0.022374 0.99961698 -0.016256001 0.026302001 0.99961698
		 -0.0085460003 0.31632301 0.94306803 -0.102779 0.26908001 0.94306803 -0.195498 0.016256001
		 0.99961698 -0.022374 0.022374 0.99961698 -0.016256001 0.26908001 0.94306803 -0.195498
		 0.195498 0.94306803 -0.26908001 0.0085460003 0.99961698 -0.026302001 0.016256001
		 0.99961698 -0.022374 0.195498 0.94306803 -0.26908001 0.102779 0.94306803 -0.316322
		 0 0.99961698 -0.027656 0.0085460003 0.99961698 -0.026302001 0.102779 0.94306803 -0.316322
		 0 0.94306803 -0.33260101 -0.0085460003 0.99961698 -0.026302001 0 0.99961698 -0.027656
		 0 0.94306803 -0.33260101 -0.102779 0.94306803 -0.31632301 -0.016256001 0.99961698
		 -0.022374 -0.0085460003 0.99961698 -0.026302001 -0.102779 0.94306803 -0.31632301
		 -0.195498 0.94306803 -0.26908001 -0.022374 0.99961698 -0.016256001 -0.016256001 0.99961698
		 -0.022374 -0.195498 0.94306803 -0.26908001 -0.26908001 0.94306803 -0.195498 -0.026302001
		 0.99961698 -0.0085460003 -0.022374 0.99961698 -0.016256001 -0.26908001 0.94306803
		 -0.195498 -0.316322 0.94306803 -0.102779 -0.027656 0.99961698 0 -0.026302001 0.99961698
		 -0.0085460003 -0.316322 0.94306803 -0.102779 -0.33260101 0.94306803 0 -0.026302001
		 0.99961698 0.0085460003 -0.027656 0.99961698 0 -0.33260101 0.94306803 0 -0.31632301
		 0.94306803 0.102779 -0.022374 0.99961698 0.016256001 -0.026302001 0.99961698 0.0085460003
		 -0.31632301 0.94306803 0.102779 -0.26908001 0.94306803 0.195498 -0.016256001 0.99961698
		 0.022374 -0.022374 0.99961698 0.016256001 -0.26908001 0.94306803 0.195498 -0.195498
		 0.94306701 0.26908001 -0.0085460003 0.99961698 0.026302001 -0.016256001 0.99961698
		 0.022374 -0.195498 0.94306701 0.26908001 -0.102779 0.94306803 0.31632301 0 0.99961698
		 0.027656 -0.0085460003 0.99961698 0.026302001 -0.102779 0.94306803 0.31632301 0 0.94306803
		 0.33260101 0.0085460003 0.99961698 0.026302001 0 0.99961698 0.027656 0 0.94306803
		 0.33260101 0.102779 0.94306803 0.31632301 0.016256001 0.99961698 0.022374 0.0085460003
		 0.99961698 0.026302001 0.102779 0.94306803 0.31632301 0.195498 0.94306803 0.26908001
		 0.022374 0.99961698 0.016256001 0.016256001 0.99961698 0.022374 0.195498 0.94306803
		 0.26908001 0.26908001 0.94306803 0.195498 0.026302001 0.99961698 0.0085460003 0.022374
		 0.99961698 0.016256001 0.26908001 0.94306803 0.195498 0.31632301 0.94306701 0.102779
		 0.027656 0.99961698 0 0.026302001 0.99961698 0.0085460003 0.31632301 0.94306701 0.102779
		 0.33260101 0.94306803 0 0.026302001 0.99961698 -0.0085460003 0.027656 0.99961698
		 0 0.33260101 0.94306803 0 0.31632301 0.94306803 -0.102779 0.26908001 0.94306803 -0.195498
		 0.31632301 0.94306803 -0.102779 0.57457101 0.79687899 -0.186689 0.48875901 0.79687899
		 -0.355104 0.195498 0.94306803 -0.26908001 0.26908001 0.94306803 -0.195498 0.48875901
		 0.79687899 -0.355104 0.355104 0.79687899 -0.48875901 0.102779 0.94306803 -0.316322
		 0.195498 0.94306803 -0.26908001 0.355104 0.79687899 -0.48875901 0.186689 0.79687899
		 -0.57457 0 0.94306803 -0.33260101 0.102779 0.94306803 -0.316322 0.186689 0.79687899
		 -0.57457 0 0.79687899 -0.60413897 -0.102779 0.94306803 -0.31632301 0 0.94306803 -0.33260101;
	setAttr ".n[498:663]" -type "float3"  0 0.79687899 -0.60413897 -0.186689 0.79687899
		 -0.57457 -0.195498 0.94306803 -0.26908001 -0.102779 0.94306803 -0.31632301 -0.186689
		 0.79687899 -0.57457 -0.355104 0.79687899 -0.48875901 -0.26908001 0.94306803 -0.195498
		 -0.195498 0.94306803 -0.26908001 -0.355104 0.79687899 -0.48875901 -0.48875901 0.79687899
		 -0.355104 -0.316322 0.94306803 -0.102779 -0.26908001 0.94306803 -0.195498 -0.48875901
		 0.79687899 -0.355104 -0.57457 0.79687899 -0.186689 -0.33260101 0.94306803 0 -0.316322
		 0.94306803 -0.102779 -0.57457 0.79687899 -0.186689 -0.60413897 0.79687899 0 -0.31632301
		 0.94306803 0.102779 -0.33260101 0.94306803 0 -0.60413897 0.79687899 0 -0.57457 0.79687899
		 0.186689 -0.26908001 0.94306803 0.195498 -0.31632301 0.94306803 0.102779 -0.57457
		 0.79687899 0.186689 -0.48875901 0.79687899 0.355104 -0.195498 0.94306701 0.26908001
		 -0.26908001 0.94306803 0.195498 -0.48875901 0.79687899 0.355104 -0.355104 0.79687899
		 0.48875901 -0.102779 0.94306803 0.31632301 -0.195498 0.94306701 0.26908001 -0.355104
		 0.79687899 0.48875901 -0.186689 0.79687899 0.57457 0 0.94306803 0.33260101 -0.102779
		 0.94306803 0.31632301 -0.186689 0.79687899 0.57457 0 0.79687899 0.60413897 0.102779
		 0.94306803 0.31632301 0 0.94306803 0.33260101 0 0.79687899 0.60413897 0.186689 0.79687899
		 0.57457101 0.195498 0.94306803 0.26908001 0.102779 0.94306803 0.31632301 0.186689
		 0.79687899 0.57457101 0.355104 0.79687899 0.48875901 0.26908001 0.94306803 0.195498
		 0.195498 0.94306803 0.26908001 0.355104 0.79687899 0.48875901 0.48875901 0.79687899
		 0.355104 0.31632301 0.94306701 0.102779 0.26908001 0.94306803 0.195498 0.48875901
		 0.79687899 0.355104 0.57457101 0.79687899 0.186689 0.33260101 0.94306803 0 0.31632301
		 0.94306701 0.102779 0.57457101 0.79687899 0.186689 0.60413897 0.79687899 1e-006 0.31632301
		 0.94306803 -0.102779 0.33260101 0.94306803 0 0.60413897 0.79687899 1e-006 0.57457101
		 0.79687899 -0.186689 0.48875901 0.79687899 -0.355104 0.57457101 0.79687899 -0.186689
		 0.77740002 0.57606101 -0.252592 0.66129601 0.57606101 -0.48045999 0.355104 0.79687899
		 -0.48875901 0.48875901 0.79687899 -0.355104 0.66129601 0.57606101 -0.48045999 0.48045999
		 0.57606101 -0.66129601 0.186689 0.79687899 -0.57457 0.355104 0.79687899 -0.48875901
		 0.48045999 0.57606101 -0.66129601 0.252592 0.57606101 -0.77740002 0 0.79687899 -0.60413897
		 0.186689 0.79687899 -0.57457 0.252592 0.57606101 -0.77740002 0 0.57606101 -0.81740701
		 -0.186689 0.79687899 -0.57457 0 0.79687899 -0.60413897 0 0.57606101 -0.81740701 -0.25259301
		 0.57606101 -0.77740002 -0.355104 0.79687899 -0.48875901 -0.186689 0.79687899 -0.57457
		 -0.25259301 0.57606101 -0.77740002 -0.48045999 0.57606101 -0.66129601 -0.48875901
		 0.79687899 -0.355104 -0.355104 0.79687899 -0.48875901 -0.48045999 0.57606101 -0.66129601
		 -0.66129601 0.57606101 -0.48045999 -0.57457 0.79687899 -0.186689 -0.48875901 0.79687899
		 -0.355104 -0.66129601 0.57606101 -0.48045999 -0.77740002 0.57606101 -0.25259301 -0.60413897
		 0.79687899 0 -0.57457 0.79687899 -0.186689 -0.77740002 0.57606101 -0.25259301 -0.81740701
		 0.57606101 0 -0.57457 0.79687899 0.186689 -0.60413897 0.79687899 0 -0.81740701 0.57606101
		 0 -0.77740002 0.57606101 0.25259301 -0.48875901 0.79687899 0.355104 -0.57457 0.79687899
		 0.186689 -0.77740002 0.57606101 0.25259301 -0.66129601 0.57606101 0.48045999 -0.355104
		 0.79687899 0.48875901 -0.48875901 0.79687899 0.355104 -0.66129601 0.57606101 0.48045999
		 -0.48045999 0.57606101 0.66129601 -0.186689 0.79687899 0.57457 -0.355104 0.79687899
		 0.48875901 -0.48045999 0.57606101 0.66129601 -0.25259301 0.57606 0.77740002 0 0.79687899
		 0.60413897 -0.186689 0.79687899 0.57457 -0.25259301 0.57606 0.77740002 0 0.57606101
		 0.81740701 0.186689 0.79687899 0.57457101 0 0.79687899 0.60413897 0 0.57606101 0.81740701
		 0.25259301 0.57606101 0.77740002 0.355104 0.79687899 0.48875901 0.186689 0.79687899
		 0.57457101 0.25259301 0.57606101 0.77740002 0.48045999 0.57606101 0.66129601 0.48875901
		 0.79687899 0.355104 0.355104 0.79687899 0.48875901 0.48045999 0.57606101 0.66129601
		 0.66129601 0.57606101 0.48045999 0.57457101 0.79687899 0.186689 0.48875901 0.79687899
		 0.355104 0.66129601 0.57606101 0.48045999 0.77740002 0.57606101 0.25259301 0.60413897
		 0.79687899 1e-006 0.57457101 0.79687899 0.186689 0.77740002 0.57606101 0.25259301
		 0.81740701 0.57606101 1e-006 0.57457101 0.79687899 -0.186689 0.60413897 0.79687899
		 1e-006 0.81740701 0.57606101 1e-006 0.77740002 0.57606101 -0.252592 0.66129601 0.57606101
		 -0.48045999 0.77740002 0.57606101 -0.252592 0.90667897 0.30190501 -0.294597 0.771267
		 0.30190501 -0.56035799 0.48045999 0.57606101 -0.66129601 0.66129601 0.57606101 -0.48045999
		 0.771267 0.30190501 -0.56035799 0.56035799 0.30190501 -0.771267 0.252592 0.57606101
		 -0.77740002 0.48045999 0.57606101 -0.66129601 0.56035799 0.30190501 -0.771267 0.294597
		 0.30190501 -0.90667802 0 0.57606101 -0.81740701 0.252592 0.57606101 -0.77740002 0.294597
		 0.30190501 -0.90667802 0 0.30190501 -0.95333803 -0.25259301 0.57606101 -0.77740002
		 0 0.57606101 -0.81740701 0 0.30190501 -0.95333803 -0.29459801 0.30190501 -0.90667802
		 -0.48045999 0.57606101 -0.66129601 -0.25259301 0.57606101 -0.77740002 -0.29459801
		 0.30190501 -0.90667802 -0.56035799 0.30190501 -0.771267;
	setAttr ".n[664:829]" -type "float3"  -0.66129601 0.57606101 -0.48045999 -0.48045999
		 0.57606101 -0.66129601 -0.56035799 0.30190501 -0.771267 -0.771267 0.30190501 -0.56035799
		 -0.77740002 0.57606101 -0.25259301 -0.66129601 0.57606101 -0.48045999 -0.771267 0.30190501
		 -0.56035799 -0.90667802 0.30190501 -0.29459801 -0.81740701 0.57606101 0 -0.77740002
		 0.57606101 -0.25259301 -0.90667802 0.30190501 -0.29459801 -0.95333803 0.30190501
		 0 -0.77740002 0.57606101 0.25259301 -0.81740701 0.57606101 0 -0.95333803 0.30190501
		 0 -0.90667802 0.30190501 0.29459801 -0.66129601 0.57606101 0.48045999 -0.77740002
		 0.57606101 0.25259301 -0.90667802 0.30190501 0.29459801 -0.771267 0.30190501 0.56035799
		 -0.48045999 0.57606101 0.66129601 -0.66129601 0.57606101 0.48045999 -0.771267 0.30190501
		 0.56035799 -0.56035799 0.30190501 0.771267 -0.25259301 0.57606 0.77740002 -0.48045999
		 0.57606101 0.66129601 -0.56035799 0.30190501 0.771267 -0.29459801 0.30190501 0.90667802
		 0 0.57606101 0.81740701 -0.25259301 0.57606 0.77740002 -0.29459801 0.30190501 0.90667802
		 0 0.30190501 0.95333803 0.25259301 0.57606101 0.77740002 0 0.57606101 0.81740701
		 0 0.30190501 0.95333803 0.29459801 0.30190501 0.90667802 0.48045999 0.57606101 0.66129601
		 0.25259301 0.57606101 0.77740002 0.29459801 0.30190501 0.90667802 0.56035799 0.30190501
		 0.771267 0.66129601 0.57606101 0.48045999 0.48045999 0.57606101 0.66129601 0.56035799
		 0.30190501 0.771267 0.771267 0.30190501 0.56035799 0.77740002 0.57606101 0.25259301
		 0.66129601 0.57606101 0.48045999 0.771267 0.30190501 0.56035799 0.90667802 0.30190501
		 0.29459801 0.81740701 0.57606101 1e-006 0.77740002 0.57606101 0.25259301 0.90667802
		 0.30190501 0.29459801 0.95333803 0.30190501 1e-006 0.77740002 0.57606101 -0.252592
		 0.81740701 0.57606101 1e-006 0.95333803 0.30190501 1e-006 0.90667897 0.30190501 -0.294597
		 0.771267 0.30190501 -0.56035799 0.90667897 0.30190501 -0.294597 0.95105702 0 -0.30901599
		 0.809017 0 -0.58778501 0.56035799 0.30190501 -0.771267 0.771267 0.30190501 -0.56035799
		 0.809017 0 -0.58778501 0.58778501 0 -0.809017 0.294597 0.30190501 -0.90667802 0.56035799
		 0.30190501 -0.771267 0.58778501 0 -0.809017 0.309017 0 -0.95105702 0 0.30190501 -0.95333803
		 0.294597 0.30190501 -0.90667802 0.309017 0 -0.95105702 0 0 -1 -0.29459801 0.30190501
		 -0.90667802 0 0.30190501 -0.95333803 0 0 -1 -0.309017 0 -0.951056 -0.56035799 0.30190501
		 -0.771267 -0.29459801 0.30190501 -0.90667802 -0.309017 0 -0.951056 -0.58778501 0
		 -0.809017 -0.771267 0.30190501 -0.56035799 -0.56035799 0.30190501 -0.771267 -0.58778501
		 0 -0.809017 -0.809017 0 -0.58778501 -0.90667802 0.30190501 -0.29459801 -0.771267
		 0.30190501 -0.56035799 -0.809017 0 -0.58778501 -0.95105702 0 -0.309017 -0.95333803
		 0.30190501 0 -0.90667802 0.30190501 -0.29459801 -0.95105702 0 -0.309017 -1 0 0 -0.90667802
		 0.30190501 0.29459801 -0.95333803 0.30190501 0 -1 0 0 -0.951056 0 0.309017 -0.771267
		 0.30190501 0.56035799 -0.90667802 0.30190501 0.29459801 -0.951056 0 0.309017 -0.809017
		 0 0.58778501 -0.56035799 0.30190501 0.771267 -0.771267 0.30190501 0.56035799 -0.809017
		 0 0.58778501 -0.58778501 0 0.809017 -0.29459801 0.30190501 0.90667802 -0.56035799
		 0.30190501 0.771267 -0.58778501 0 0.809017 -0.309017 0 0.95105702 0 0.30190501 0.95333803
		 -0.29459801 0.30190501 0.90667802 -0.309017 0 0.95105702 0 0 1 0.29459801 0.30190501
		 0.90667802 0 0.30190501 0.95333803 0 0 1 0.309017 0 0.951056 0.56035799 0.30190501
		 0.771267 0.29459801 0.30190501 0.90667802 0.309017 0 0.951056 0.58778501 0 0.809017
		 0.771267 0.30190501 0.56035799 0.56035799 0.30190501 0.771267 0.58778501 0 0.809017
		 0.809017 0 0.58778501 0.90667802 0.30190501 0.29459801 0.771267 0.30190501 0.56035799
		 0.809017 0 0.58778501 0.95105702 0 0.309017 0.95333803 0.30190501 1e-006 0.90667802
		 0.30190501 0.29459801 0.95105702 0 0.309017 1 0 1e-006 0.90667897 0.30190501 -0.294597
		 0.95333803 0.30190501 1e-006 1 0 1e-006 0.95105702 0 -0.30901599 0.809017 0 -0.58778501
		 0.95105702 0 -0.30901599 0.90667897 -0.30190501 -0.294597 0.771267 -0.30190501 -0.56035799
		 0.58778501 0 -0.809017 0.809017 0 -0.58778501 0.771267 -0.30190501 -0.56035799 0.56035799
		 -0.30190501 -0.771267 0.309017 0 -0.95105702 0.58778501 0 -0.809017 0.56035799 -0.30190501
		 -0.771267 0.294597 -0.30190501 -0.90667802 0 0 -1 0.309017 0 -0.95105702 0.294597
		 -0.30190501 -0.90667802 0 -0.30190501 -0.95333803 -0.309017 0 -0.951056 0 0 -1 0
		 -0.30190501 -0.95333803 -0.29459801 -0.30190501 -0.90667802 -0.58778501 0 -0.809017
		 -0.309017 0 -0.951056 -0.29459801 -0.30190501 -0.90667802 -0.56035799 -0.30190501
		 -0.771267 -0.809017 0 -0.58778501 -0.58778501 0 -0.809017 -0.56035799 -0.30190501
		 -0.771267 -0.771267 -0.30190501 -0.56035799 -0.95105702 0 -0.309017 -0.809017 0 -0.58778501;
	setAttr ".n[830:995]" -type "float3"  -0.771267 -0.30190501 -0.56035799 -0.90667802
		 -0.30190501 -0.29459801 -1 0 0 -0.95105702 0 -0.309017 -0.90667802 -0.30190501 -0.29459801
		 -0.95333803 -0.30190501 0 -0.951056 0 0.309017 -1 0 0 -0.95333803 -0.30190501 0 -0.90667802
		 -0.30190501 0.29459801 -0.809017 0 0.58778501 -0.951056 0 0.309017 -0.90667802 -0.30190501
		 0.29459801 -0.771267 -0.30190501 0.56035799 -0.58778501 0 0.809017 -0.809017 0 0.58778501
		 -0.771267 -0.30190501 0.56035799 -0.56035799 -0.30190501 0.771267 -0.309017 0 0.95105702
		 -0.58778501 0 0.809017 -0.56035799 -0.30190501 0.771267 -0.29459801 -0.30190501 0.90667802
		 0 0 1 -0.309017 0 0.95105702 -0.29459801 -0.30190501 0.90667802 0 -0.30190501 0.95333803
		 0.309017 0 0.951056 0 0 1 0 -0.30190501 0.95333803 0.29459801 -0.30190501 0.90667802
		 0.58778501 0 0.809017 0.309017 0 0.951056 0.29459801 -0.30190501 0.90667802 0.56035799
		 -0.30190501 0.771267 0.809017 0 0.58778501 0.58778501 0 0.809017 0.56035799 -0.30190501
		 0.771267 0.771267 -0.30190501 0.56035799 0.95105702 0 0.309017 0.809017 0 0.58778501
		 0.771267 -0.30190501 0.56035799 0.90667802 -0.30190501 0.29459801 1 0 1e-006 0.95105702
		 0 0.309017 0.90667802 -0.30190501 0.29459801 0.95333803 -0.30190501 1e-006 0.95105702
		 0 -0.30901599 1 0 1e-006 0.95333803 -0.30190501 1e-006 0.90667897 -0.30190501 -0.294597
		 0.771267 -0.30190501 -0.56035799 0.90667897 -0.30190501 -0.294597 0.77740097 -0.57606
		 -0.252592 0.66129601 -0.57606 -0.48045999 0.56035799 -0.30190501 -0.771267 0.771267
		 -0.30190501 -0.56035799 0.66129601 -0.57606 -0.48045999 0.48045999 -0.57606 -0.66129601
		 0.294597 -0.30190501 -0.90667802 0.56035799 -0.30190501 -0.771267 0.48045999 -0.57606
		 -0.66129601 0.25259301 -0.57606 -0.77740002 0 -0.30190501 -0.95333803 0.294597 -0.30190501
		 -0.90667802 0.25259301 -0.57606 -0.77740002 0 -0.57606 -0.81740701 -0.29459801 -0.30190501
		 -0.90667802 0 -0.30190501 -0.95333803 0 -0.57606 -0.81740701 -0.25259301 -0.57606
		 -0.77740002 -0.56035799 -0.30190501 -0.771267 -0.29459801 -0.30190501 -0.90667802
		 -0.25259301 -0.57606 -0.77740002 -0.48045999 -0.57606 -0.66129601 -0.771267 -0.30190501
		 -0.56035799 -0.56035799 -0.30190501 -0.771267 -0.48045999 -0.57606 -0.66129601 -0.66129702
		 -0.57606 -0.48045999 -0.90667802 -0.30190501 -0.29459801 -0.771267 -0.30190501 -0.56035799
		 -0.66129702 -0.57606 -0.48045999 -0.77740002 -0.57606 -0.25259301 -0.95333803 -0.30190501
		 0 -0.90667802 -0.30190501 -0.29459801 -0.77740002 -0.57606 -0.25259301 -0.81740701
		 -0.57606 0 -0.90667802 -0.30190501 0.29459801 -0.95333803 -0.30190501 0 -0.81740701
		 -0.57606 0 -0.77740002 -0.57606101 0.25259301 -0.771267 -0.30190501 0.56035799 -0.90667802
		 -0.30190501 0.29459801 -0.77740002 -0.57606101 0.25259301 -0.66129601 -0.57606 0.48045999
		 -0.56035799 -0.30190501 0.771267 -0.771267 -0.30190501 0.56035799 -0.66129601 -0.57606
		 0.48045999 -0.48045999 -0.57606 0.66129601 -0.29459801 -0.30190501 0.90667802 -0.56035799
		 -0.30190501 0.771267 -0.48045999 -0.57606 0.66129601 -0.25259301 -0.57606 0.77740097
		 0 -0.30190501 0.95333803 -0.29459801 -0.30190501 0.90667802 -0.25259301 -0.57606
		 0.77740097 0 -0.57606 0.81740701 0.29459801 -0.30190501 0.90667802 0 -0.30190501
		 0.95333803 0 -0.57606 0.81740701 0.25259301 -0.57606 0.77740002 0.56035799 -0.30190501
		 0.771267 0.29459801 -0.30190501 0.90667802 0.25259301 -0.57606 0.77740002 0.48045999
		 -0.57606 0.66129601 0.771267 -0.30190501 0.56035799 0.56035799 -0.30190501 0.771267
		 0.48045999 -0.57606 0.66129601 0.66129601 -0.57606 0.48045999 0.90667802 -0.30190501
		 0.29459801 0.771267 -0.30190501 0.56035799 0.66129601 -0.57606 0.48045999 0.77740097
		 -0.57606 0.25259301 0.95333803 -0.30190501 1e-006 0.90667802 -0.30190501 0.29459801
		 0.77740097 -0.57606 0.25259301 0.81740701 -0.57606 1e-006 0.90667897 -0.30190501
		 -0.294597 0.95333803 -0.30190501 1e-006 0.81740701 -0.57606 1e-006 0.77740097 -0.57606
		 -0.252592 0.66129601 -0.57606 -0.48045999 0.77740097 -0.57606 -0.252592 0.57457101
		 -0.79687899 -0.186689 0.48875901 -0.79687899 -0.355104 0.48045999 -0.57606 -0.66129601
		 0.66129601 -0.57606 -0.48045999 0.48875901 -0.79687899 -0.355104 0.355104 -0.79687899
		 -0.48875901 0.25259301 -0.57606 -0.77740002 0.48045999 -0.57606 -0.66129601 0.355104
		 -0.79687899 -0.48875901 0.186689 -0.79687899 -0.57457101 0 -0.57606 -0.81740701 0.25259301
		 -0.57606 -0.77740002 0.186689 -0.79687899 -0.57457101 0 -0.79687899 -0.60413897 -0.25259301
		 -0.57606 -0.77740002 0 -0.57606 -0.81740701 0 -0.79687899 -0.60413897 -0.186689 -0.79687899
		 -0.57457101 -0.48045999 -0.57606 -0.66129601 -0.25259301 -0.57606 -0.77740002 -0.186689
		 -0.79687899 -0.57457101 -0.355104 -0.79687899 -0.48875901 -0.66129702 -0.57606 -0.48045999
		 -0.48045999 -0.57606 -0.66129601 -0.355104 -0.79687899 -0.48875901 -0.48875901 -0.79687899
		 -0.355104 -0.77740002 -0.57606 -0.25259301 -0.66129702 -0.57606 -0.48045999 -0.48875901
		 -0.79687899 -0.355104 -0.57457101 -0.79687899 -0.186689 -0.81740701 -0.57606 0 -0.77740002
		 -0.57606 -0.25259301 -0.57457101 -0.79687899 -0.186689 -0.60413897 -0.79687899 0;
	setAttr ".n[996:1161]" -type "float3"  -0.77740002 -0.57606101 0.25259301 -0.81740701
		 -0.57606 0 -0.60413897 -0.79687899 0 -0.57457101 -0.79687899 0.186689 -0.66129601
		 -0.57606 0.48045999 -0.77740002 -0.57606101 0.25259301 -0.57457101 -0.79687899 0.186689
		 -0.48875901 -0.79687798 0.355104 -0.48045999 -0.57606 0.66129601 -0.66129601 -0.57606
		 0.48045999 -0.48875901 -0.79687798 0.355104 -0.355104 -0.79687899 0.48875901 -0.25259301
		 -0.57606 0.77740097 -0.48045999 -0.57606 0.66129601 -0.355104 -0.79687899 0.48875901
		 -0.186689 -0.79687899 0.57457101 0 -0.57606 0.81740701 -0.25259301 -0.57606 0.77740097
		 -0.186689 -0.79687899 0.57457101 0 -0.79687899 0.60413897 0.25259301 -0.57606 0.77740002
		 0 -0.57606 0.81740701 0 -0.79687899 0.60413897 0.186689 -0.79687899 0.57457101 0.48045999
		 -0.57606 0.66129601 0.25259301 -0.57606 0.77740002 0.186689 -0.79687899 0.57457101
		 0.355104 -0.79687798 0.48875901 0.66129601 -0.57606 0.48045999 0.48045999 -0.57606
		 0.66129601 0.355104 -0.79687798 0.48875901 0.48875901 -0.79687798 0.355104 0.77740097
		 -0.57606 0.25259301 0.66129601 -0.57606 0.48045999 0.48875901 -0.79687798 0.355104
		 0.57457101 -0.79687798 0.186689 0.81740701 -0.57606 1e-006 0.77740097 -0.57606 0.25259301
		 0.57457101 -0.79687798 0.186689 0.60413998 -0.79687899 1e-006 0.77740097 -0.57606
		 -0.252592 0.81740701 -0.57606 1e-006 0.60413998 -0.79687899 1e-006 0.57457101 -0.79687899
		 -0.186689 0.48875901 -0.79687899 -0.355104 0.57457101 -0.79687899 -0.186689 0.31632301
		 -0.94306701 -0.102779 0.26908001 -0.94306803 -0.195498 0.355104 -0.79687899 -0.48875901
		 0.48875901 -0.79687899 -0.355104 0.26908001 -0.94306803 -0.195498 0.195498 -0.94306803
		 -0.26908001 0.186689 -0.79687899 -0.57457101 0.355104 -0.79687899 -0.48875901 0.195498
		 -0.94306803 -0.26908001 0.102779 -0.94306803 -0.31632301 0 -0.79687899 -0.60413897
		 0.186689 -0.79687899 -0.57457101 0.102779 -0.94306803 -0.31632301 0 -0.94306803 -0.33260101
		 -0.186689 -0.79687899 -0.57457101 0 -0.79687899 -0.60413897 0 -0.94306803 -0.33260101
		 -0.102779 -0.94306803 -0.31632301 -0.355104 -0.79687899 -0.48875901 -0.186689 -0.79687899
		 -0.57457101 -0.102779 -0.94306803 -0.31632301 -0.195498 -0.94306803 -0.26908001 -0.48875901
		 -0.79687899 -0.355104 -0.355104 -0.79687899 -0.48875901 -0.195498 -0.94306803 -0.26908001
		 -0.26908001 -0.94306803 -0.195498 -0.57457101 -0.79687899 -0.186689 -0.48875901 -0.79687899
		 -0.355104 -0.26908001 -0.94306803 -0.195498 -0.31632301 -0.94306701 -0.102779 -0.60413897
		 -0.79687899 0 -0.57457101 -0.79687899 -0.186689 -0.31632301 -0.94306701 -0.102779
		 -0.33260101 -0.94306803 0 -0.57457101 -0.79687899 0.186689 -0.60413897 -0.79687899
		 0 -0.33260101 -0.94306803 0 -0.31632301 -0.94306701 0.102779 -0.48875901 -0.79687798
		 0.355104 -0.57457101 -0.79687899 0.186689 -0.31632301 -0.94306701 0.102779 -0.26908001
		 -0.94306701 0.195498 -0.355104 -0.79687899 0.48875901 -0.48875901 -0.79687798 0.355104
		 -0.26908001 -0.94306701 0.195498 -0.195498 -0.94306701 0.26908001 -0.186689 -0.79687899
		 0.57457101 -0.355104 -0.79687899 0.48875901 -0.195498 -0.94306701 0.26908001 -0.102779
		 -0.94306701 0.31632301 0 -0.79687899 0.60413897 -0.186689 -0.79687899 0.57457101
		 -0.102779 -0.94306701 0.31632301 0 -0.94306803 0.33260101 0.186689 -0.79687899 0.57457101
		 0 -0.79687899 0.60413897 0 -0.94306803 0.33260101 0.102779 -0.94306701 0.31632301
		 0.355104 -0.79687798 0.48875901 0.186689 -0.79687899 0.57457101 0.102779 -0.94306701
		 0.31632301 0.195498 -0.94306803 0.26908001 0.48875901 -0.79687798 0.355104 0.355104
		 -0.79687798 0.48875901 0.195498 -0.94306803 0.26908001 0.26908001 -0.94306803 0.195498
		 0.57457101 -0.79687798 0.186689 0.48875901 -0.79687798 0.355104 0.26908001 -0.94306803
		 0.195498 0.31632301 -0.94306701 0.10278 0.60413998 -0.79687899 1e-006 0.57457101
		 -0.79687798 0.186689 0.31632301 -0.94306701 0.10278 0.33260101 -0.94306701 0 0.57457101
		 -0.79687899 -0.186689 0.60413998 -0.79687899 1e-006 0.33260101 -0.94306701 0 0.31632301
		 -0.94306701 -0.102779 0.26908001 -0.94306803 -0.195498 0.31632301 -0.94306701 -0.102779
		 0.026303001 -0.99961698 -0.0085460003 0.022374 -0.99961698 -0.016256001 0.195498
		 -0.94306803 -0.26908001 0.26908001 -0.94306803 -0.195498 0.022374 -0.99961698 -0.016256001
		 0.016256001 -0.99961698 -0.022374 0.102779 -0.94306803 -0.31632301 0.195498 -0.94306803
		 -0.26908001 0.016256001 -0.99961698 -0.022374 0.0085460003 -0.99961698 -0.026303001
		 0 -0.94306803 -0.33260101 0.102779 -0.94306803 -0.31632301 0.0085460003 -0.99961698
		 -0.026303001 0 -0.99961698 -0.027656 -0.102779 -0.94306803 -0.31632301 0 -0.94306803
		 -0.33260101 0 -0.99961698 -0.027656 -0.0085460003 -0.99961698 -0.026302001 -0.195498
		 -0.94306803 -0.26908001 -0.102779 -0.94306803 -0.31632301 -0.0085460003 -0.99961698
		 -0.026302001 -0.016256001 -0.99961799 -0.022374 -0.26908001 -0.94306803 -0.195498
		 -0.195498 -0.94306803 -0.26908001 -0.016256001 -0.99961799 -0.022374 -0.022374 -0.99961698
		 -0.016256001 -0.31632301 -0.94306701 -0.102779 -0.26908001 -0.94306803 -0.195498
		 -0.022374 -0.99961698 -0.016256001 -0.026303001 -0.99961698 -0.0085460003 -0.33260101
		 -0.94306803 0 -0.31632301 -0.94306701 -0.102779 -0.026303001 -0.99961698 -0.0085460003
		 -0.027656 -0.99961698 0 -0.31632301 -0.94306701 0.102779 -0.33260101 -0.94306803
		 0 -0.027656 -0.99961698 0 -0.026303001 -0.99961698 0.0085460003 -0.26908001 -0.94306701
		 0.195498 -0.31632301 -0.94306701 0.102779;
	setAttr ".n[1162:1327]" -type "float3"  -0.026303001 -0.99961698 0.0085460003
		 -0.022374 -0.99961698 0.016256001 -0.195498 -0.94306701 0.26908001 -0.26908001 -0.94306701
		 0.195498 -0.022374 -0.99961698 0.016256001 -0.016256001 -0.99961698 0.022374 -0.102779
		 -0.94306701 0.31632301 -0.195498 -0.94306701 0.26908001 -0.016256001 -0.99961698
		 0.022374 -0.0085460003 -0.99961698 0.026303001 0 -0.94306803 0.33260101 -0.102779
		 -0.94306701 0.31632301 -0.0085460003 -0.99961698 0.026303001 0 -0.99961698 0.027656
		 0.102779 -0.94306701 0.31632301 0 -0.94306803 0.33260101 0 -0.99961698 0.027656 0.0085460003
		 -0.99961698 0.026303001 0.195498 -0.94306803 0.26908001 0.102779 -0.94306701 0.31632301
		 0.0085460003 -0.99961698 0.026303001 0.016256001 -0.99961698 0.022374 0.26908001
		 -0.94306803 0.195498 0.195498 -0.94306803 0.26908001 0.016256001 -0.99961698 0.022374
		 0.022374 -0.99961698 0.016256001 0.31632301 -0.94306701 0.10278 0.26908001 -0.94306803
		 0.195498 0.022374 -0.99961698 0.016256001 0.026303001 -0.99961698 0.0085460003 0.33260101
		 -0.94306701 0 0.31632301 -0.94306701 0.10278 0.026303001 -0.99961698 0.0085460003
		 0.027656 -0.99961698 0 0.31632301 -0.94306701 -0.102779 0.33260101 -0.94306701 0
		 0.027656 -0.99961698 0 0.026303001 -0.99961698 -0.0085460003 0.022374 -0.99961698
		 -0.016256001 0.026303001 -0.99961698 -0.0085460003 -0.26821199 -0.95941001 0.087146997
		 -0.228155 -0.95941001 0.165764 0.016256001 -0.99961698 -0.022374 0.022374 -0.99961698
		 -0.016256001 -0.228155 -0.95941001 0.165764 -0.165764 -0.95941001 0.228155 0.0085460003
		 -0.99961698 -0.026303001 0.016256001 -0.99961698 -0.022374 -0.165764 -0.95941001
		 0.228155 -0.087146997 -0.95941001 0.26821199 0 -0.99961698 -0.027656 0.0085460003
		 -0.99961698 -0.026303001 -0.087146997 -0.95941001 0.26821199 0 -0.95941001 0.282015
		 -0.0085460003 -0.99961698 -0.026302001 0 -0.99961698 -0.027656 0 -0.95941001 0.282015
		 0.087146997 -0.95941001 0.26821199 -0.016256001 -0.99961799 -0.022374 -0.0085460003
		 -0.99961698 -0.026302001 0.087146997 -0.95941001 0.26821199 0.165764 -0.95941001
		 0.228155 -0.022374 -0.99961698 -0.016256001 -0.016256001 -0.99961799 -0.022374 0.165764
		 -0.95941001 0.228155 0.228155 -0.95941001 0.165764 -0.026303001 -0.99961698 -0.0085460003
		 -0.022374 -0.99961698 -0.016256001 0.228155 -0.95941001 0.165764 0.26821199 -0.95941001
		 0.087146997 -0.027656 -0.99961698 0 -0.026303001 -0.99961698 -0.0085460003 0.26821199
		 -0.95941001 0.087146997 0.282015 -0.95941001 0 -0.026303001 -0.99961698 0.0085460003
		 -0.027656 -0.99961698 0 0.282015 -0.95941001 0 0.26821199 -0.95941001 -0.087146997
		 -0.022374 -0.99961698 0.016256001 -0.026303001 -0.99961698 0.0085460003 0.26821199
		 -0.95941001 -0.087146997 0.228155 -0.95941001 -0.165764 -0.016256001 -0.99961698
		 0.022374 -0.022374 -0.99961698 0.016256001 0.228155 -0.95941001 -0.165764 0.165764
		 -0.95941001 -0.228155 -0.0085460003 -0.99961698 0.026303001 -0.016256001 -0.99961698
		 0.022374 0.165764 -0.95941001 -0.228155 0.087146997 -0.95941001 -0.26821199 0 -0.99961698
		 0.027656 -0.0085460003 -0.99961698 0.026303001 0.087146997 -0.95941001 -0.26821199
		 0 -0.95941001 -0.282015 0.0085460003 -0.99961698 0.026303001 0 -0.99961698 0.027656
		 0 -0.95941001 -0.282015 -0.087146997 -0.95941001 -0.26821199 0.016256001 -0.99961698
		 0.022374 0.0085460003 -0.99961698 0.026303001 -0.087146997 -0.95941001 -0.26821199
		 -0.165764 -0.95941001 -0.228155 0.022374 -0.99961698 0.016256001 0.016256001 -0.99961698
		 0.022374 -0.165764 -0.95941001 -0.228155 -0.228155 -0.95941001 -0.165764 0.026303001
		 -0.99961698 0.0085460003 0.022374 -0.99961698 0.016256001 -0.228155 -0.95941001 -0.165764
		 -0.26821199 -0.95941001 -0.087146997 0.027656 -0.99961698 0 0.026303001 -0.99961698
		 0.0085460003 -0.26821199 -0.95941001 -0.087146997 -0.282015 -0.95941001 0 0.026303001
		 -0.99961698 -0.0085460003 0.027656 -0.99961698 0 -0.282015 -0.95941001 0 -0.26821199
		 -0.95941001 0.087146997 -0.228155 -0.95941001 0.165764 -0.26821199 -0.95941001 0.087146997
		 -0.53865802 -0.82414502 0.17501999 -0.45820999 -0.82414502 0.33290899 -0.165764 -0.95941001
		 0.228155 -0.228155 -0.95941001 0.165764 -0.45820999 -0.82414502 0.33290899 -0.33290899
		 -0.82414502 0.45820999 -0.087146997 -0.95941001 0.26821199 -0.165764 -0.95941001
		 0.228155 -0.33290899 -0.82414502 0.45820999 -0.17502099 -0.82414502 0.53865802 0
		 -0.95941001 0.282015 -0.087146997 -0.95941001 0.26821199 -0.17502099 -0.82414502
		 0.53865802 0 -0.82414502 0.56637901 0.087146997 -0.95941001 0.26821199 0 -0.95941001
		 0.282015 0 -0.82414502 0.56637901 0.17502099 -0.82414502 0.53865802 0.165764 -0.95941001
		 0.228155 0.087146997 -0.95941001 0.26821199 0.17502099 -0.82414502 0.53865802 0.33290899
		 -0.82414502 0.45820999 0.228155 -0.95941001 0.165764 0.165764 -0.95941001 0.228155
		 0.33290899 -0.82414502 0.45820999 0.45820999 -0.82414502 0.33290899 0.26821199 -0.95941001
		 0.087146997 0.228155 -0.95941001 0.165764 0.45820999 -0.82414502 0.33290899 0.53865802
		 -0.82414502 0.17502099 0.282015 -0.95941001 0 0.26821199 -0.95941001 0.087146997
		 0.53865802 -0.82414502 0.17502099 0.56637901 -0.82414502 0 0.26821199 -0.95941001
		 -0.087146997 0.282015 -0.95941001 0 0.56637901 -0.82414502 0 0.53865802 -0.82414502
		 -0.17502099 0.228155 -0.95941001 -0.165764 0.26821199 -0.95941001 -0.087146997 0.53865802
		 -0.82414502 -0.17502099 0.45820999 -0.82414502 -0.33290899 0.165764 -0.95941001 -0.228155
		 0.228155 -0.95941001 -0.165764 0.45820999 -0.82414502 -0.33290899 0.33290899 -0.82414502
		 -0.45820999;
	setAttr ".n[1328:1493]" -type "float3"  0.087146997 -0.95941001 -0.26821199 0.165764
		 -0.95941001 -0.228155 0.33290899 -0.82414502 -0.45820999 0.17502099 -0.82414502 -0.53865802
		 0 -0.95941001 -0.282015 0.087146997 -0.95941001 -0.26821199 0.17502099 -0.82414502
		 -0.53865802 0 -0.82414502 -0.56637901 -0.087146997 -0.95941001 -0.26821199 0 -0.95941001
		 -0.282015 0 -0.82414502 -0.56637901 -0.17502099 -0.82414502 -0.53865898 -0.165764
		 -0.95941001 -0.228155 -0.087146997 -0.95941001 -0.26821199 -0.17502099 -0.82414502
		 -0.53865898 -0.33290899 -0.82414502 -0.45820999 -0.228155 -0.95941001 -0.165764 -0.165764
		 -0.95941001 -0.228155 -0.33290899 -0.82414502 -0.45820999 -0.45820999 -0.82414502
		 -0.33290899 -0.26821199 -0.95941001 -0.087146997 -0.228155 -0.95941001 -0.165764
		 -0.45820999 -0.82414502 -0.33290899 -0.53865802 -0.82414502 -0.17502099 -0.282015
		 -0.95941001 0 -0.26821199 -0.95941001 -0.087146997 -0.53865802 -0.82414502 -0.17502099
		 -0.56637901 -0.82414502 -1e-006 -0.26821199 -0.95941001 0.087146997 -0.282015 -0.95941001
		 0 -0.56637901 -0.82414502 -1e-006 -0.53865802 -0.82414502 0.17501999 -0.45820999
		 -0.82414502 0.33290899 -0.53865802 -0.82414502 0.17501999 -0.75760198 -0.60452098
		 0.246159 -0.64445502 -0.60452002 0.46822399 -0.33290899 -0.82414502 0.45820999 -0.45820999
		 -0.82414502 0.33290899 -0.64445502 -0.60452002 0.46822399 -0.46822399 -0.60452002
		 0.64445502 -0.17502099 -0.82414502 0.53865802 -0.33290899 -0.82414502 0.45820999
		 -0.46822399 -0.60452002 0.64445502 -0.24616 -0.60452002 0.75760198 0 -0.82414502
		 0.56637901 -0.17502099 -0.82414502 0.53865802 -0.24616 -0.60452002 0.75760198 0 -0.60452002
		 0.79658997 0.17502099 -0.82414502 0.53865802 0 -0.82414502 0.56637901 0 -0.60452002
		 0.79658997 0.24616 -0.60452002 0.75760198 0.33290899 -0.82414502 0.45820999 0.17502099
		 -0.82414502 0.53865802 0.24616 -0.60452002 0.75760198 0.46822399 -0.60452002 0.64445502
		 0.45820999 -0.82414502 0.33290899 0.33290899 -0.82414502 0.45820999 0.46822399 -0.60452002
		 0.64445502 0.64445502 -0.60452002 0.46822399 0.53865802 -0.82414502 0.17502099 0.45820999
		 -0.82414502 0.33290899 0.64445502 -0.60452002 0.46822399 0.75760198 -0.60452002 0.24616
		 0.56637901 -0.82414502 0 0.53865802 -0.82414502 0.17502099 0.75760198 -0.60452002
		 0.24616 0.79658997 -0.60452002 0 0.53865802 -0.82414502 -0.17502099 0.56637901 -0.82414502
		 0 0.79658997 -0.60452002 0 0.75760198 -0.60452002 -0.24616 0.45820999 -0.82414502
		 -0.33290899 0.53865802 -0.82414502 -0.17502099 0.75760198 -0.60452002 -0.24616 0.64445502
		 -0.60452002 -0.46822399 0.33290899 -0.82414502 -0.45820999 0.45820999 -0.82414502
		 -0.33290899 0.64445502 -0.60452002 -0.46822399 0.46822399 -0.60452002 -0.64445502
		 0.17502099 -0.82414502 -0.53865802 0.33290899 -0.82414502 -0.45820999 0.46822399
		 -0.60452002 -0.64445502 0.24616 -0.60452002 -0.75760198 0 -0.82414502 -0.56637901
		 0.17502099 -0.82414502 -0.53865802 0.24616 -0.60452002 -0.75760198 0 -0.60452002
		 -0.79658997 -0.17502099 -0.82414502 -0.53865898 0 -0.82414502 -0.56637901 0 -0.60452002
		 -0.79658997 -0.24616 -0.60452002 -0.75760198 -0.33290899 -0.82414502 -0.45820999
		 -0.17502099 -0.82414502 -0.53865898 -0.24616 -0.60452002 -0.75760198 -0.46822399
		 -0.60452002 -0.64445502 -0.45820999 -0.82414502 -0.33290899 -0.33290899 -0.82414502
		 -0.45820999 -0.46822399 -0.60452002 -0.64445502 -0.64445502 -0.60452002 -0.46822399
		 -0.53865802 -0.82414502 -0.17502099 -0.45820999 -0.82414502 -0.33290899 -0.64445502
		 -0.60452002 -0.46822399 -0.75760198 -0.60452002 -0.24616 -0.56637901 -0.82414502
		 -1e-006 -0.53865802 -0.82414502 -0.17502099 -0.75760198 -0.60452002 -0.24616 -0.79658997
		 -0.60452002 -1e-006 -0.53865802 -0.82414502 0.17501999 -0.56637901 -0.82414502 -1e-006
		 -0.79658997 -0.60452002 -1e-006 -0.75760198 -0.60452098 0.246159 -0.64445502 -0.60452002
		 0.46822399 -0.75760198 -0.60452098 0.246159 -0.90098298 -0.32020101 0.29274601 -0.76642197
		 -0.32020101 0.55683798 -0.46822399 -0.60452002 0.64445502 -0.64445502 -0.60452002
		 0.46822399 -0.76642197 -0.32020101 0.55683798 -0.55683798 -0.32020101 0.76642197
		 -0.24616 -0.60452002 0.75760198 -0.46822399 -0.60452002 0.64445502 -0.55683798 -0.32020101
		 0.76642197 -0.29274699 -0.32020101 0.90098298 0 -0.60452002 0.79658997 -0.24616 -0.60452002
		 0.75760198 -0.29274699 -0.32020101 0.90098298 0 -0.32020101 0.94734901 0.24616 -0.60452002
		 0.75760198 0 -0.60452002 0.79658997 0 -0.32020101 0.94734901 0.29274699 -0.32020101
		 0.90098298 0.46822399 -0.60452002 0.64445502 0.24616 -0.60452002 0.75760198 0.29274699
		 -0.32020101 0.90098298 0.55683798 -0.32020101 0.76642197 0.64445502 -0.60452002 0.46822399
		 0.46822399 -0.60452002 0.64445502 0.55683798 -0.32020101 0.76642197 0.76642197 -0.32020101
		 0.55683798 0.75760198 -0.60452002 0.24616 0.64445502 -0.60452002 0.46822399 0.76642197
		 -0.32020101 0.55683798 0.90098298 -0.32020101 0.29274699 0.79658997 -0.60452002 0
		 0.75760198 -0.60452002 0.24616 0.90098298 -0.32020101 0.29274699 0.94735003 -0.32020101
		 0 0.75760198 -0.60452002 -0.24616 0.79658997 -0.60452002 0 0.94735003 -0.32020101
		 0 0.90098298 -0.32020101 -0.29274699 0.64445502 -0.60452002 -0.46822399 0.75760198
		 -0.60452002 -0.24616 0.90098298 -0.32020101 -0.29274699 0.76642197 -0.32020101 -0.55683798
		 0.46822399 -0.60452002 -0.64445502 0.64445502 -0.60452002 -0.46822399 0.76642197
		 -0.32020101 -0.55683798 0.55683798 -0.32020101 -0.76642197 0.24616 -0.60452002 -0.75760198
		 0.46822399 -0.60452002 -0.64445502 0.55683798 -0.32020101 -0.76642197 0.29274699
		 -0.32020101 -0.90098298 0 -0.60452002 -0.79658997 0.24616 -0.60452002 -0.75760198;
	setAttr ".n[1494:1599]" -type "float3"  0.29274699 -0.32020101 -0.90098298 0
		 -0.32020101 -0.94735003 -0.24616 -0.60452002 -0.75760198 0 -0.60452002 -0.79658997
		 0 -0.32020101 -0.94735003 -0.29274699 -0.32020101 -0.90098298 -0.46822399 -0.60452002
		 -0.64445502 -0.24616 -0.60452002 -0.75760198 -0.29274699 -0.32020101 -0.90098298
		 -0.55683798 -0.32020101 -0.76642197 -0.64445502 -0.60452002 -0.46822399 -0.46822399
		 -0.60452002 -0.64445502 -0.55683798 -0.32020101 -0.76642197 -0.76642197 -0.32020101
		 -0.55683798 -0.75760198 -0.60452002 -0.24616 -0.64445502 -0.60452002 -0.46822399
		 -0.76642197 -0.32020101 -0.55683798 -0.90098298 -0.32020101 -0.29274699 -0.79658997
		 -0.60452002 -1e-006 -0.75760198 -0.60452002 -0.24616 -0.90098298 -0.32020101 -0.29274699
		 -0.94735003 -0.32020101 -1e-006 -0.75760198 -0.60452098 0.246159 -0.79658997 -0.60452002
		 -1e-006 -0.94735003 -0.32020101 -1e-006 -0.90098298 -0.32020101 0.29274601 -0.76642197
		 -0.32020101 0.55683798 -0.90098298 -0.32020101 0.29274601 -0.95105702 1e-006 0.30901599
		 -0.809017 1e-006 0.58778501 -0.55683798 -0.32020101 0.76642197 -0.76642197 -0.32020101
		 0.55683798 -0.809017 1e-006 0.58778501 -0.58778501 1e-006 0.809017 -0.29274699 -0.32020101
		 0.90098298 -0.55683798 -0.32020101 0.76642197 -0.58778501 1e-006 0.809017 -0.309017
		 1e-006 0.95105702 0 -0.32020101 0.94734901 -0.29274699 -0.32020101 0.90098298 -0.309017
		 1e-006 0.95105702 0 1e-006 1 0.29274699 -0.32020101 0.90098298 0 -0.32020101 0.94734901
		 0 1e-006 1 0.309017 1e-006 0.951056 0.55683798 -0.32020101 0.76642197 0.29274699
		 -0.32020101 0.90098298 0.309017 1e-006 0.951056 0.58778501 1e-006 0.809017 0.76642197
		 -0.32020101 0.55683798 0.55683798 -0.32020101 0.76642197 0.58778501 1e-006 0.809017
		 0.809017 1e-006 0.58778501 0.90098298 -0.32020101 0.29274699 0.76642197 -0.32020101
		 0.55683798 0.809017 1e-006 0.58778501 0.95105702 1e-006 0.309017 0.94735003 -0.32020101
		 0 0.90098298 -0.32020101 0.29274699 0.95105702 1e-006 0.309017 1 1e-006 0 0.90098298
		 -0.32020101 -0.29274699 0.94735003 -0.32020101 0 1 1e-006 0 0.951056 1e-006 -0.309017
		 0.76642197 -0.32020101 -0.55683798 0.90098298 -0.32020101 -0.29274699 0.951056 1e-006
		 -0.309017 0.809017 1e-006 -0.58778501 0.55683798 -0.32020101 -0.76642197 0.76642197
		 -0.32020101 -0.55683798 0.809017 1e-006 -0.58778501 0.58778501 1e-006 -0.809017 0.29274699
		 -0.32020101 -0.90098298 0.55683798 -0.32020101 -0.76642197 0.58778501 1e-006 -0.809017
		 0.309017 1e-006 -0.95105702 0 -0.32020101 -0.94735003 0.29274699 -0.32020101 -0.90098298
		 0.309017 1e-006 -0.95105702 0 1e-006 -1 -0.29274699 -0.32020101 -0.90098298 0 -0.32020101
		 -0.94735003 0 1e-006 -1 -0.309017 1e-006 -0.951056 -0.55683798 -0.32020101 -0.76642197
		 -0.29274699 -0.32020101 -0.90098298 -0.309017 1e-006 -0.951056 -0.58778501 1e-006
		 -0.809017 -0.76642197 -0.32020101 -0.55683798 -0.55683798 -0.32020101 -0.76642197
		 -0.58778501 1e-006 -0.809017 -0.809017 1e-006 -0.58778501 -0.90098298 -0.32020101
		 -0.29274699 -0.76642197 -0.32020101 -0.55683798 -0.809017 1e-006 -0.58778501 -0.95105702
		 1e-006 -0.309017 -0.94735003 -0.32020101 -1e-006 -0.90098298 -0.32020101 -0.29274699
		 -0.95105702 1e-006 -0.309017 -1 1e-006 -1e-006 -0.90098298 -0.32020101 0.29274601
		 -0.94735003 -0.32020101 -1e-006 -1 1e-006 -1e-006 -0.95105702 1e-006 0.30901599;
	setAttr -s 400 -ch 1600 ".fc[0:399]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 4 -4 5 6
		mu 0 4 4 0 3 5
		f 4 7 -7 8 9
		mu 0 4 6 4 5 7
		f 4 10 -10 11 12
		mu 0 4 8 6 7 9
		f 4 13 -13 14 15
		mu 0 4 10 8 9 11
		f 4 16 -16 17 18
		mu 0 4 12 10 11 13
		f 4 19 -19 20 21
		mu 0 4 14 12 13 15
		f 4 22 -22 23 24
		mu 0 4 16 14 15 17
		f 4 25 -25 26 27
		mu 0 4 18 16 17 19
		f 4 28 -28 29 30
		mu 0 4 20 18 19 21
		f 4 31 -31 32 33
		mu 0 4 22 20 21 23
		f 4 34 -34 35 36
		mu 0 4 24 22 23 25
		f 4 37 -37 38 39
		mu 0 4 26 24 25 27
		f 4 40 -40 41 42
		mu 0 4 28 26 27 29
		f 4 43 -43 44 45
		mu 0 4 30 28 29 31
		f 4 46 -46 47 48
		mu 0 4 32 30 31 33
		f 4 49 -49 50 51
		mu 0 4 34 32 33 35
		f 4 52 -52 53 54
		mu 0 4 36 34 35 37
		f 4 55 -55 56 57
		mu 0 4 38 36 37 39
		f 4 58 -58 59 -2
		mu 0 4 40 38 39 41
		f 4 -3 60 61 62
		mu 0 4 3 2 42 43
		f 4 -6 -63 63 64
		mu 0 4 5 3 43 44
		f 4 -9 -65 65 66
		mu 0 4 7 5 44 45
		f 4 -12 -67 67 68
		mu 0 4 9 7 45 46
		f 4 -15 -69 69 70
		mu 0 4 11 9 46 47
		f 4 -18 -71 71 72
		mu 0 4 13 11 47 48
		f 4 -21 -73 73 74
		mu 0 4 15 13 48 49
		f 4 -24 -75 75 76
		mu 0 4 17 15 49 50
		f 4 -27 -77 77 78
		mu 0 4 19 17 50 51
		f 4 -30 -79 79 80
		mu 0 4 21 19 51 52
		f 4 -33 -81 81 82
		mu 0 4 23 21 52 53
		f 4 -36 -83 83 84
		mu 0 4 25 23 53 54
		f 4 -39 -85 85 86
		mu 0 4 27 25 54 55
		f 4 -42 -87 87 88
		mu 0 4 29 27 55 56
		f 4 -45 -89 89 90
		mu 0 4 31 29 56 57
		f 4 -48 -91 91 92
		mu 0 4 33 31 57 58
		f 4 -51 -93 93 94
		mu 0 4 35 33 58 59
		f 4 -54 -95 95 96
		mu 0 4 37 35 59 60
		f 4 -57 -97 97 98
		mu 0 4 39 37 60 61
		f 4 -60 -99 99 -61
		mu 0 4 41 39 61 62
		f 4 -62 100 101 102
		mu 0 4 43 42 63 64
		f 4 -64 -103 103 104
		mu 0 4 44 43 64 65
		f 4 -66 -105 105 106
		mu 0 4 45 44 65 66
		f 4 -68 -107 107 108
		mu 0 4 46 45 66 67
		f 4 -70 -109 109 110
		mu 0 4 47 46 67 68
		f 4 -72 -111 111 112
		mu 0 4 48 47 68 69
		f 4 -74 -113 113 114
		mu 0 4 49 48 69 70
		f 4 -76 -115 115 116
		mu 0 4 50 49 70 71
		f 4 -78 -117 117 118
		mu 0 4 51 50 71 72
		f 4 -80 -119 119 120
		mu 0 4 52 51 72 73
		f 4 -82 -121 121 122
		mu 0 4 53 52 73 74
		f 4 -84 -123 123 124
		mu 0 4 54 53 74 75
		f 4 -86 -125 125 126
		mu 0 4 55 54 75 76
		f 4 -88 -127 127 128
		mu 0 4 56 55 76 77
		f 4 -90 -129 129 130
		mu 0 4 57 56 77 78
		f 4 -92 -131 131 132
		mu 0 4 58 57 78 79
		f 4 -94 -133 133 134
		mu 0 4 59 58 79 80
		f 4 -96 -135 135 136
		mu 0 4 60 59 80 81
		f 4 -98 -137 137 138
		mu 0 4 61 60 81 82
		f 4 -100 -139 139 -101
		mu 0 4 62 61 82 83
		f 4 -102 140 141 142
		mu 0 4 64 63 84 85
		f 4 -104 -143 143 144
		mu 0 4 65 64 85 86
		f 4 -106 -145 145 146
		mu 0 4 66 65 86 87
		f 4 -108 -147 147 148
		mu 0 4 67 66 87 88
		f 4 -110 -149 149 150
		mu 0 4 68 67 88 89
		f 4 -112 -151 151 152
		mu 0 4 69 68 89 90
		f 4 -114 -153 153 154
		mu 0 4 70 69 90 91
		f 4 -116 -155 155 156
		mu 0 4 71 70 91 92
		f 4 -118 -157 157 158
		mu 0 4 72 71 92 93
		f 4 -120 -159 159 160
		mu 0 4 73 72 93 94
		f 4 -122 -161 161 162
		mu 0 4 74 73 94 95
		f 4 -124 -163 163 164
		mu 0 4 75 74 95 96
		f 4 -126 -165 165 166
		mu 0 4 76 75 96 97
		f 4 -128 -167 167 168
		mu 0 4 77 76 97 98
		f 4 -130 -169 169 170
		mu 0 4 78 77 98 99
		f 4 -132 -171 171 172
		mu 0 4 79 78 99 100
		f 4 -134 -173 173 174
		mu 0 4 80 79 100 101
		f 4 -136 -175 175 176
		mu 0 4 81 80 101 102
		f 4 -138 -177 177 178
		mu 0 4 82 81 102 103
		f 4 -140 -179 179 -141
		mu 0 4 83 82 103 104
		f 4 -142 180 181 182
		mu 0 4 85 84 105 106
		f 4 -144 -183 183 184
		mu 0 4 86 85 106 107
		f 4 -146 -185 185 186
		mu 0 4 87 86 107 108
		f 4 -148 -187 187 188
		mu 0 4 88 87 108 109
		f 4 -150 -189 189 190
		mu 0 4 89 88 109 110
		f 4 -152 -191 191 192
		mu 0 4 90 89 110 111
		f 4 -154 -193 193 194
		mu 0 4 91 90 111 112
		f 4 -156 -195 195 196
		mu 0 4 92 91 112 113
		f 4 -158 -197 197 198
		mu 0 4 93 92 113 114
		f 4 -160 -199 199 200
		mu 0 4 94 93 114 115
		f 4 -162 -201 201 202
		mu 0 4 95 94 115 116
		f 4 -164 -203 203 204
		mu 0 4 96 95 116 117
		f 4 -166 -205 205 206
		mu 0 4 97 96 117 118
		f 4 -168 -207 207 208
		mu 0 4 98 97 118 119
		f 4 -170 -209 209 210
		mu 0 4 99 98 119 120
		f 4 -172 -211 211 212
		mu 0 4 100 99 120 121
		f 4 -174 -213 213 214
		mu 0 4 101 100 121 122
		f 4 -176 -215 215 216
		mu 0 4 102 101 122 123
		f 4 -178 -217 217 218
		mu 0 4 103 102 123 124
		f 4 -180 -219 219 -181
		mu 0 4 104 103 124 125
		f 4 -182 220 221 222
		mu 0 4 106 105 126 127
		f 4 -184 -223 223 224
		mu 0 4 107 106 127 128
		f 4 -186 -225 225 226
		mu 0 4 108 107 128 129
		f 4 -188 -227 227 228
		mu 0 4 109 108 129 130
		f 4 -190 -229 229 230
		mu 0 4 110 109 130 131
		f 4 -192 -231 231 232
		mu 0 4 111 110 131 132
		f 4 -194 -233 233 234
		mu 0 4 112 111 132 133
		f 4 -196 -235 235 236
		mu 0 4 113 112 133 134
		f 4 -198 -237 237 238
		mu 0 4 114 113 134 135
		f 4 -200 -239 239 240
		mu 0 4 115 114 135 136
		f 4 -202 -241 241 242
		mu 0 4 116 115 136 137
		f 4 -204 -243 243 244
		mu 0 4 117 116 137 138
		f 4 -206 -245 245 246
		mu 0 4 118 117 138 139
		f 4 -208 -247 247 248
		mu 0 4 119 118 139 140
		f 4 -210 -249 249 250
		mu 0 4 120 119 140 141
		f 4 -212 -251 251 252
		mu 0 4 121 120 141 142
		f 4 -214 -253 253 254
		mu 0 4 122 121 142 143
		f 4 -216 -255 255 256
		mu 0 4 123 122 143 144
		f 4 -218 -257 257 258
		mu 0 4 124 123 144 145
		f 4 -220 -259 259 -221
		mu 0 4 125 124 145 146
		f 4 -222 260 261 262
		mu 0 4 127 126 147 148
		f 4 -224 -263 263 264
		mu 0 4 128 127 148 149
		f 4 -226 -265 265 266
		mu 0 4 129 128 149 150
		f 4 -228 -267 267 268
		mu 0 4 130 129 150 151
		f 4 -230 -269 269 270
		mu 0 4 131 130 151 152
		f 4 -232 -271 271 272
		mu 0 4 132 131 152 153
		f 4 -234 -273 273 274
		mu 0 4 133 132 153 154
		f 4 -236 -275 275 276
		mu 0 4 134 133 154 155
		f 4 -238 -277 277 278
		mu 0 4 135 134 155 156
		f 4 -240 -279 279 280
		mu 0 4 136 135 156 157
		f 4 -242 -281 281 282
		mu 0 4 137 136 157 158
		f 4 -244 -283 283 284
		mu 0 4 138 137 158 159
		f 4 -246 -285 285 286
		mu 0 4 139 138 159 160
		f 4 -248 -287 287 288
		mu 0 4 140 139 160 161
		f 4 -250 -289 289 290
		mu 0 4 141 140 161 162
		f 4 -252 -291 291 292
		mu 0 4 142 141 162 163
		f 4 -254 -293 293 294
		mu 0 4 143 142 163 164
		f 4 -256 -295 295 296
		mu 0 4 144 143 164 165
		f 4 -258 -297 297 298
		mu 0 4 145 144 165 166
		f 4 -260 -299 299 -261
		mu 0 4 146 145 166 167
		f 4 -262 300 301 302
		mu 0 4 148 147 168 169
		f 4 -264 -303 303 304
		mu 0 4 149 148 169 170
		f 4 -266 -305 305 306
		mu 0 4 150 149 170 171
		f 4 -268 -307 307 308
		mu 0 4 151 150 171 172
		f 4 -270 -309 309 310
		mu 0 4 152 151 172 173
		f 4 -272 -311 311 312
		mu 0 4 153 152 173 174
		f 4 -274 -313 313 314
		mu 0 4 154 153 174 175
		f 4 -276 -315 315 316
		mu 0 4 155 154 175 176
		f 4 -278 -317 317 318
		mu 0 4 156 155 176 177
		f 4 -280 -319 319 320
		mu 0 4 157 156 177 178
		f 4 -282 -321 321 322
		mu 0 4 158 157 178 179
		f 4 -284 -323 323 324
		mu 0 4 159 158 179 180
		f 4 -286 -325 325 326
		mu 0 4 160 159 180 181
		f 4 -288 -327 327 328
		mu 0 4 161 160 181 182
		f 4 -290 -329 329 330
		mu 0 4 162 161 182 183
		f 4 -292 -331 331 332
		mu 0 4 163 162 183 184
		f 4 -294 -333 333 334
		mu 0 4 164 163 184 185
		f 4 -296 -335 335 336
		mu 0 4 165 164 185 186
		f 4 -298 -337 337 338
		mu 0 4 166 165 186 187
		f 4 -300 -339 339 -301
		mu 0 4 167 166 187 188
		f 4 -302 340 341 342
		mu 0 4 169 168 189 190
		f 4 -304 -343 343 344
		mu 0 4 170 169 190 191
		f 4 -306 -345 345 346
		mu 0 4 171 170 191 192
		f 4 -308 -347 347 348
		mu 0 4 172 171 192 193
		f 4 -310 -349 349 350
		mu 0 4 173 172 193 194
		f 4 -312 -351 351 352
		mu 0 4 174 173 194 195
		f 4 -314 -353 353 354
		mu 0 4 175 174 195 196
		f 4 -316 -355 355 356
		mu 0 4 176 175 196 197
		f 4 -318 -357 357 358
		mu 0 4 177 176 197 198
		f 4 -320 -359 359 360
		mu 0 4 178 177 198 199
		f 4 -322 -361 361 362
		mu 0 4 179 178 199 200
		f 4 -324 -363 363 364
		mu 0 4 180 179 200 201
		f 4 -326 -365 365 366
		mu 0 4 181 180 201 202
		f 4 -328 -367 367 368
		mu 0 4 182 181 202 203
		f 4 -330 -369 369 370
		mu 0 4 183 182 203 204
		f 4 -332 -371 371 372
		mu 0 4 184 183 204 205
		f 4 -334 -373 373 374
		mu 0 4 185 184 205 206
		f 4 -336 -375 375 376
		mu 0 4 186 185 206 207
		f 4 -338 -377 377 378
		mu 0 4 187 186 207 208
		f 4 -340 -379 379 -341
		mu 0 4 188 187 208 209
		f 4 -342 380 381 382
		mu 0 4 190 189 210 211
		f 4 -344 -383 383 384
		mu 0 4 191 190 211 212
		f 4 -346 -385 385 386
		mu 0 4 192 191 212 213
		f 4 -348 -387 387 388
		mu 0 4 193 192 213 214
		f 4 -350 -389 389 390
		mu 0 4 194 193 214 215
		f 4 -352 -391 391 392
		mu 0 4 195 194 215 216
		f 4 -354 -393 393 394
		mu 0 4 196 195 216 217
		f 4 -356 -395 395 396
		mu 0 4 197 196 217 218
		f 4 -358 -397 397 398
		mu 0 4 198 197 218 219
		f 4 -360 -399 399 400
		mu 0 4 199 198 219 220
		f 4 -362 -401 401 402
		mu 0 4 200 199 220 221
		f 4 -364 -403 403 404
		mu 0 4 201 200 221 222
		f 4 -366 -405 405 406
		mu 0 4 202 201 222 223
		f 4 -368 -407 407 408
		mu 0 4 203 202 223 224
		f 4 -370 -409 409 410
		mu 0 4 204 203 224 225
		f 4 -372 -411 411 412
		mu 0 4 205 204 225 226
		f 4 -374 -413 413 414
		mu 0 4 206 205 226 227
		f 4 -376 -415 415 416
		mu 0 4 207 206 227 228
		f 4 -378 -417 417 418
		mu 0 4 208 207 228 229
		f 4 -380 -419 419 -381
		mu 0 4 209 208 229 230
		f 4 -382 420 421 422
		mu 0 4 211 210 231 232
		f 4 -384 -423 423 424
		mu 0 4 212 211 232 233
		f 4 -386 -425 425 426
		mu 0 4 213 212 233 234
		f 4 -388 -427 427 428
		mu 0 4 214 213 234 235
		f 4 -390 -429 429 430
		mu 0 4 215 214 235 236
		f 4 -392 -431 431 432
		mu 0 4 216 215 236 237
		f 4 -394 -433 433 434
		mu 0 4 217 216 237 238
		f 4 -396 -435 435 436
		mu 0 4 218 217 238 239
		f 4 -398 -437 437 438
		mu 0 4 219 218 239 240
		f 4 -400 -439 439 440
		mu 0 4 220 219 240 241
		f 4 -402 -441 441 442
		mu 0 4 221 220 241 242
		f 4 -404 -443 443 444
		mu 0 4 222 221 242 243
		f 4 -406 -445 445 446
		mu 0 4 223 222 243 244
		f 4 -408 -447 447 448
		mu 0 4 224 223 244 245
		f 4 -410 -449 449 450
		mu 0 4 225 224 245 246
		f 4 -412 -451 451 452
		mu 0 4 226 225 246 247
		f 4 -414 -453 453 454
		mu 0 4 227 226 247 248
		f 4 -416 -455 455 456
		mu 0 4 228 227 248 249
		f 4 -418 -457 457 458
		mu 0 4 229 228 249 250
		f 4 -420 -459 459 -421
		mu 0 4 230 229 250 251
		f 4 -422 460 461 462
		mu 0 4 232 231 252 253
		f 4 -424 -463 463 464
		mu 0 4 233 232 253 254
		f 4 -426 -465 465 466
		mu 0 4 234 233 254 255
		f 4 -428 -467 467 468
		mu 0 4 235 234 255 256
		f 4 -430 -469 469 470
		mu 0 4 236 235 256 257
		f 4 -432 -471 471 472
		mu 0 4 237 236 257 258
		f 4 -434 -473 473 474
		mu 0 4 238 237 258 259
		f 4 -436 -475 475 476
		mu 0 4 239 238 259 260
		f 4 -438 -477 477 478
		mu 0 4 240 239 260 261
		f 4 -440 -479 479 480
		mu 0 4 241 240 261 262
		f 4 -442 -481 481 482
		mu 0 4 242 241 262 263
		f 4 -444 -483 483 484
		mu 0 4 243 242 263 264
		f 4 -446 -485 485 486
		mu 0 4 244 243 264 265
		f 4 -448 -487 487 488
		mu 0 4 245 244 265 266
		f 4 -450 -489 489 490
		mu 0 4 246 245 266 267
		f 4 -452 -491 491 492
		mu 0 4 247 246 267 268
		f 4 -454 -493 493 494
		mu 0 4 248 247 268 269
		f 4 -456 -495 495 496
		mu 0 4 249 248 269 270
		f 4 -458 -497 497 498
		mu 0 4 250 249 270 271
		f 4 -460 -499 499 -461
		mu 0 4 251 250 271 272
		f 4 -462 500 501 502
		mu 0 4 253 252 273 274
		f 4 -464 -503 503 504
		mu 0 4 254 253 274 275
		f 4 -466 -505 505 506
		mu 0 4 255 254 275 276
		f 4 -468 -507 507 508
		mu 0 4 256 255 276 277
		f 4 -470 -509 509 510
		mu 0 4 257 256 277 278
		f 4 -472 -511 511 512
		mu 0 4 258 257 278 279
		f 4 -474 -513 513 514
		mu 0 4 259 258 279 280
		f 4 -476 -515 515 516
		mu 0 4 260 259 280 281
		f 4 -478 -517 517 518
		mu 0 4 261 260 281 282
		f 4 -480 -519 519 520
		mu 0 4 262 261 282 283
		f 4 -482 -521 521 522
		mu 0 4 263 262 283 284
		f 4 -484 -523 523 524
		mu 0 4 264 263 284 285
		f 4 -486 -525 525 526
		mu 0 4 265 264 285 286
		f 4 -488 -527 527 528
		mu 0 4 266 265 286 287
		f 4 -490 -529 529 530
		mu 0 4 267 266 287 288
		f 4 -492 -531 531 532
		mu 0 4 268 267 288 289
		f 4 -494 -533 533 534
		mu 0 4 269 268 289 290
		f 4 -496 -535 535 536
		mu 0 4 270 269 290 291
		f 4 -498 -537 537 538
		mu 0 4 271 270 291 292
		f 4 -500 -539 539 -501
		mu 0 4 272 271 292 293
		f 4 -502 540 541 542
		mu 0 4 274 273 294 295
		f 4 -504 -543 543 544
		mu 0 4 275 274 295 296
		f 4 -506 -545 545 546
		mu 0 4 276 275 296 297
		f 4 -508 -547 547 548
		mu 0 4 277 276 297 298
		f 4 -510 -549 549 550
		mu 0 4 278 277 298 299
		f 4 -512 -551 551 552
		mu 0 4 279 278 299 300
		f 4 -514 -553 553 554
		mu 0 4 280 279 300 301
		f 4 -516 -555 555 556
		mu 0 4 281 280 301 302
		f 4 -518 -557 557 558
		mu 0 4 282 281 302 303
		f 4 -520 -559 559 560
		mu 0 4 283 282 303 304
		f 4 -522 -561 561 562
		mu 0 4 284 283 304 305
		f 4 -524 -563 563 564
		mu 0 4 285 284 305 306
		f 4 -526 -565 565 566
		mu 0 4 286 285 306 307
		f 4 -528 -567 567 568
		mu 0 4 287 286 307 308
		f 4 -530 -569 569 570
		mu 0 4 288 287 308 309
		f 4 -532 -571 571 572
		mu 0 4 289 288 309 310
		f 4 -534 -573 573 574
		mu 0 4 290 289 310 311
		f 4 -536 -575 575 576
		mu 0 4 291 290 311 312
		f 4 -538 -577 577 578
		mu 0 4 292 291 312 313
		f 4 -540 -579 579 -541
		mu 0 4 293 292 313 314
		f 4 -542 580 581 582
		mu 0 4 295 294 315 316
		f 4 -544 -583 583 584
		mu 0 4 296 295 316 317
		f 4 -546 -585 585 586
		mu 0 4 297 296 317 318
		f 4 -548 -587 587 588
		mu 0 4 298 297 318 319
		f 4 -550 -589 589 590
		mu 0 4 299 298 319 320
		f 4 -552 -591 591 592
		mu 0 4 300 299 320 321
		f 4 -554 -593 593 594
		mu 0 4 301 300 321 322
		f 4 -556 -595 595 596
		mu 0 4 302 301 322 323
		f 4 -558 -597 597 598
		mu 0 4 303 302 323 324
		f 4 -560 -599 599 600
		mu 0 4 304 303 324 325
		f 4 -562 -601 601 602
		mu 0 4 305 304 325 326
		f 4 -564 -603 603 604
		mu 0 4 306 305 326 327
		f 4 -566 -605 605 606
		mu 0 4 307 306 327 328
		f 4 -568 -607 607 608
		mu 0 4 308 307 328 329
		f 4 -570 -609 609 610
		mu 0 4 309 308 329 330
		f 4 -572 -611 611 612
		mu 0 4 310 309 330 331
		f 4 -574 -613 613 614
		mu 0 4 311 310 331 332
		f 4 -576 -615 615 616
		mu 0 4 312 311 332 333
		f 4 -578 -617 617 618
		mu 0 4 313 312 333 334
		f 4 -580 -619 619 -581
		mu 0 4 314 313 334 335
		f 4 -582 620 621 622
		mu 0 4 316 315 336 337
		f 4 -584 -623 623 624
		mu 0 4 317 316 337 338
		f 4 -586 -625 625 626
		mu 0 4 318 317 338 339
		f 4 -588 -627 627 628
		mu 0 4 319 318 339 340
		f 4 -590 -629 629 630
		mu 0 4 320 319 340 341
		f 4 -592 -631 631 632
		mu 0 4 321 320 341 342
		f 4 -594 -633 633 634
		mu 0 4 322 321 342 343
		f 4 -596 -635 635 636
		mu 0 4 323 322 343 344
		f 4 -598 -637 637 638
		mu 0 4 324 323 344 345
		f 4 -600 -639 639 640
		mu 0 4 325 324 345 346
		f 4 -602 -641 641 642
		mu 0 4 326 325 346 347
		f 4 -604 -643 643 644
		mu 0 4 327 326 347 348
		f 4 -606 -645 645 646
		mu 0 4 328 327 348 349
		f 4 -608 -647 647 648
		mu 0 4 329 328 349 350
		f 4 -610 -649 649 650
		mu 0 4 330 329 350 351
		f 4 -612 -651 651 652
		mu 0 4 331 330 351 352
		f 4 -614 -653 653 654
		mu 0 4 332 331 352 353
		f 4 -616 -655 655 656
		mu 0 4 333 332 353 354
		f 4 -618 -657 657 658
		mu 0 4 334 333 354 355
		f 4 -620 -659 659 -621
		mu 0 4 335 334 355 356
		f 4 -622 660 661 662
		mu 0 4 337 336 357 358
		f 4 -624 -663 663 664
		mu 0 4 338 337 358 359
		f 4 -626 -665 665 666
		mu 0 4 339 338 359 360
		f 4 -628 -667 667 668
		mu 0 4 340 339 360 361
		f 4 -630 -669 669 670
		mu 0 4 341 340 361 362
		f 4 -632 -671 671 672
		mu 0 4 342 341 362 363
		f 4 -634 -673 673 674
		mu 0 4 343 342 363 364
		f 4 -636 -675 675 676
		mu 0 4 344 343 364 365
		f 4 -638 -677 677 678
		mu 0 4 345 344 365 366
		f 4 -640 -679 679 680
		mu 0 4 346 345 366 367
		f 4 -642 -681 681 682
		mu 0 4 347 346 367 368
		f 4 -644 -683 683 684
		mu 0 4 348 347 368 369
		f 4 -646 -685 685 686
		mu 0 4 349 348 369 370
		f 4 -648 -687 687 688
		mu 0 4 350 349 370 371
		f 4 -650 -689 689 690
		mu 0 4 351 350 371 372
		f 4 -652 -691 691 692
		mu 0 4 352 351 372 373
		f 4 -654 -693 693 694
		mu 0 4 353 352 373 374
		f 4 -656 -695 695 696
		mu 0 4 354 353 374 375
		f 4 -658 -697 697 698
		mu 0 4 355 354 375 376
		f 4 -660 -699 699 -661
		mu 0 4 356 355 376 377
		f 4 -662 700 701 702
		mu 0 4 358 357 378 379
		f 4 -664 -703 703 704
		mu 0 4 359 358 379 380
		f 4 -666 -705 705 706
		mu 0 4 360 359 380 381
		f 4 -668 -707 707 708
		mu 0 4 361 360 381 382
		f 4 -670 -709 709 710
		mu 0 4 362 361 382 383
		f 4 -672 -711 711 712
		mu 0 4 363 362 383 384
		f 4 -674 -713 713 714
		mu 0 4 364 363 384 385
		f 4 -676 -715 715 716
		mu 0 4 365 364 385 386
		f 4 -678 -717 717 718
		mu 0 4 366 365 386 387
		f 4 -680 -719 719 720
		mu 0 4 367 366 387 388
		f 4 -682 -721 721 722
		mu 0 4 368 367 388 389
		f 4 -684 -723 723 724
		mu 0 4 369 368 389 390
		f 4 -686 -725 725 726
		mu 0 4 370 369 390 391
		f 4 -688 -727 727 728
		mu 0 4 371 370 391 392
		f 4 -690 -729 729 730
		mu 0 4 372 371 392 393
		f 4 -692 -731 731 732
		mu 0 4 373 372 393 394
		f 4 -694 -733 733 734
		mu 0 4 374 373 394 395
		f 4 -696 -735 735 736
		mu 0 4 375 374 395 396
		f 4 -698 -737 737 738
		mu 0 4 376 375 396 397
		f 4 -700 -739 739 -701
		mu 0 4 377 376 397 398
		f 4 -702 740 741 742
		mu 0 4 379 378 399 400
		f 4 -704 -743 743 744
		mu 0 4 380 379 400 401
		f 4 -706 -745 745 746
		mu 0 4 381 380 401 402
		f 4 -708 -747 747 748
		mu 0 4 382 381 402 403
		f 4 -710 -749 749 750
		mu 0 4 383 382 403 404
		f 4 -712 -751 751 752
		mu 0 4 384 383 404 405
		f 4 -714 -753 753 754
		mu 0 4 385 384 405 406
		f 4 -716 -755 755 756
		mu 0 4 386 385 406 407
		f 4 -718 -757 757 758
		mu 0 4 387 386 407 408
		f 4 -720 -759 759 760
		mu 0 4 388 387 408 409
		f 4 -722 -761 761 762
		mu 0 4 389 388 409 410
		f 4 -724 -763 763 764
		mu 0 4 390 389 410 411
		f 4 -726 -765 765 766
		mu 0 4 391 390 411 412
		f 4 -728 -767 767 768
		mu 0 4 392 391 412 413
		f 4 -730 -769 769 770
		mu 0 4 393 392 413 414
		f 4 -732 -771 771 772
		mu 0 4 394 393 414 415
		f 4 -734 -773 773 774
		mu 0 4 395 394 415 416
		f 4 -736 -775 775 776
		mu 0 4 396 395 416 417
		f 4 -738 -777 777 778
		mu 0 4 397 396 417 418
		f 4 -740 -779 779 -741
		mu 0 4 398 397 418 419
		f 4 -742 780 -1 781
		mu 0 4 400 399 420 421
		f 4 -744 -782 -5 782
		mu 0 4 401 400 421 422
		f 4 -746 -783 -8 783
		mu 0 4 402 401 422 423
		f 4 -748 -784 -11 784
		mu 0 4 403 402 423 424
		f 4 -750 -785 -14 785
		mu 0 4 404 403 424 425
		f 4 -752 -786 -17 786
		mu 0 4 405 404 425 426
		f 4 -754 -787 -20 787
		mu 0 4 406 405 426 427
		f 4 -756 -788 -23 788
		mu 0 4 407 406 427 428
		f 4 -758 -789 -26 789
		mu 0 4 408 407 428 429
		f 4 -760 -790 -29 790
		mu 0 4 409 408 429 430
		f 4 -762 -791 -32 791
		mu 0 4 410 409 430 431
		f 4 -764 -792 -35 792
		mu 0 4 411 410 431 432
		f 4 -766 -793 -38 793
		mu 0 4 412 411 432 433
		f 4 -768 -794 -41 794
		mu 0 4 413 412 433 434
		f 4 -770 -795 -44 795
		mu 0 4 414 413 434 435
		f 4 -772 -796 -47 796
		mu 0 4 415 414 435 436
		f 4 -774 -797 -50 797
		mu 0 4 416 415 436 437
		f 4 -776 -798 -53 798
		mu 0 4 417 416 437 438
		f 4 -778 -799 -56 799
		mu 0 4 418 417 438 439
		f 4 -780 -800 -59 -781
		mu 0 4 419 418 439 440;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
createNode transform -n "geom:pCylinder1" -p "group1";
	rename -uid "57330238-4F28-E978-E2B8-A89D4462A90A";
createNode mesh -n "geom:pCylinder1Shape" -p "geom:pCylinder1";
	rename -uid "578C53E4-4452-6809-ADE0-3A82B0C1DEB0";
	setAttr -k off ".v";
	setAttr ".iog[0].og[0].gcl" -type "componentList" 1 "f[0:59]";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 90 ".uvst[0].uvsp[0:89]" -type "float2" 0.18602601 0.001992
		 0.231987 0.001992 0.231987 0.331734 0.18602601 0.331734 0.26846099 0.001992 0.26846099
		 0.331734 0.46755201 0.331734 0.42159101 0.331734 0.42159101 0.001992 0.46755201 0.001992
		 0.37064299 0.331734 0.37064299 0.001992 0.319695 0.331734 0.319695 0.001992 0.273734
		 0.331734 0.273734 0.001992 0.47432399 0.001992 0.51079899 0.001992 0.51079899 0.331734
		 0.47432399 0.331734 0.55676001 0.001992 0.55676001 0.331734 0.60770702 0.001992 0.60770702
		 0.331734 0.65865499 0.001992 0.65865499 0.331734 0.70461601 0.001992 0.70461601 0.331734
		 0.74109101 0.001992 0.74109101 0.331734 0.655083 0.33512899 0.70104301 0.33512899
		 0.70104301 0.66487098 0.655083 0.66487098 0.75199097 0.33512899 0.75199097 0.66487098
		 0.802939 0.33512899 0.802939 0.66487098 0.84890002 0.33512899 0.84890002 0.66487098
		 0.001694 0.001992 0.038169 0.001992 0.038169 0.331734 0.001694 0.331734 0.084129997
		 0.001992 0.084129997 0.331734 0.135078 0.001992 0.135078 0.331734 0.61837697 0.40309101
		 0.64179498 0.44905201 0.48499301 0.5 0.58190203 0.36661699 0.535941 0.34319901 0.48499301
		 0.33512899 0.43404499 0.34319901 0.38808399 0.36661699 0.35161 0.40309101 0.32819101
		 0.44905201 0.320122 0.5 0.32819101 0.55094802 0.35161 0.59690899 0.38808399 0.63338399
		 0.43404499 0.656802 0.48499301 0.66487098 0.535941 0.656802 0.58190203 0.63338399
		 0.61837602 0.59690899 0.64179498 0.55094802 0.64986402 0.5 0.323367 0.884085 0.29994899
		 0.93004602 0.166565 0.83313698 0.26347399 0.96652001 0.217513 0.98993897 0.166565
		 0.99800801 0.115617 0.98993897 0.069656998 0.96652001 0.033181999 0.93004602 0.0097639998
		 0.884085 0.001694 0.83313698 0.0097639998 0.78218901 0.033181999 0.73622799 0.069656998
		 0.699754 0.115617 0.67633599 0.166565 0.668266 0.217513 0.67633599 0.26347399 0.699754
		 0.29994899 0.73622799 0.323367 0.78218901 0.33143601 0.83313698;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 42 ".vt[0:41]"  7.31925106 -0.081991002 -5.45879889 6.95033312 -0.081991002 -6.18284178
		 6.37572908 -0.081991002 -6.75744486 5.65168619 -0.081991002 -7.1263628 4.84907818 -0.081991002 -7.25348377
		 4.046471119 -0.081991002 -7.1263628 3.32242799 -0.081991002 -6.75744486 2.74782491 -0.081991002 -6.18284082
		 2.37890697 -0.081991002 -5.45879889 2.25178599 -0.081991002 -4.65619087 2.37890697 -0.081991002 -3.85358405
		 2.74782491 -0.081991002 -3.12954092 3.32242799 -0.081991002 -2.55493808 4.046471119 -0.081991002 -2.1860199
		 4.84907818 -0.081991002 -2.058898926 5.65168524 -0.081991002 -2.1860199 6.37572813 -0.081991002 -2.55493808
		 6.95033121 -0.081991002 -3.12954092 7.31924915 -0.081991002 -3.85358405 7.44637012 -0.081991002 -4.65619087
		 7.31925106 5.11259079 -5.45879889 6.95033312 5.11259079 -6.18284178 6.37572908 5.11259079 -6.75744486
		 5.65168619 5.11259079 -7.1263628 4.84907818 5.11259079 -7.25348377 4.046471119 5.11259079 -7.1263628
		 3.32242799 5.11259079 -6.75744486 2.74782491 5.11259079 -6.18284082 2.37890697 5.11259079 -5.45879889
		 2.25178599 5.11259079 -4.65619087 2.37890697 5.11259079 -3.85358405 2.74782491 5.11259079 -3.12954092
		 3.32242799 5.11259079 -2.55493808 4.046471119 5.11259079 -2.1860199 4.84907818 5.11259079 -2.058898926
		 5.65168524 5.11259079 -2.1860199 6.37572813 5.11259079 -2.55493808 6.95033121 5.11259079 -3.12954092
		 7.31924915 5.11259079 -3.85358405 7.44637012 5.11259079 -4.65619087 4.84907818 -0.081991002 -4.65619087
		 4.84907818 5.11259079 -4.65619087;
	setAttr -s 100 ".ed[0:99]"  0 1 0 1 21 0 21 20 0 20 0 0 1 2 0 2 22 0
		 22 21 0 2 3 0 3 23 0 23 22 0 3 4 0 4 24 0 24 23 0 4 5 0 5 25 0 25 24 0 5 6 0 6 26 0
		 26 25 0 6 7 0 7 27 0 27 26 0 7 8 0 8 28 0 28 27 0 8 9 0 9 29 0 29 28 0 9 10 0 10 30 0
		 30 29 0 10 11 0 11 31 0 31 30 0 11 12 0 12 32 0 32 31 0 12 13 0 13 33 0 33 32 0 13 14 0
		 14 34 0 34 33 0 14 15 0 15 35 0 35 34 0 15 16 0 16 36 0 36 35 0 16 17 0 17 37 0 37 36 0
		 17 18 0 18 38 0 38 37 0 18 19 0 19 39 0 39 38 0 19 0 0 20 39 0 0 40 0 40 1 0 40 2 0
		 40 3 0 40 4 0 40 5 0 40 6 0 40 7 0 40 8 0 40 9 0 40 10 0 40 11 0 40 12 0 40 13 0
		 40 14 0 40 15 0 40 16 0 40 17 0 40 18 0 40 19 0 21 41 0 41 20 0 22 41 0 23 41 0 24 41 0
		 25 41 0 26 41 0 27 41 0 28 41 0 29 41 0 30 41 0 31 41 0 32 41 0 33 41 0 34 41 0 35 41 0
		 36 41 0 37 41 0 38 41 0 39 41 0;
	setAttr -s 200 ".n";
	setAttr ".n[0:165]" -type "float3"  1e+020 1e+020 1e+020 1e+020 1e+020 1e+020
		 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 0.809017 0 -0.58778501 0.58778501 0 -0.809017
		 0.58778501 0 -0.809017 0.809017 0 -0.58778501 0.58778501 0 -0.809017 0.309017 0 -0.95105702
		 0.309017 0 -0.95105702 0.58778501 0 -0.809017 0.309017 0 -0.95105702 0 0 -1 0 0 -1
		 0.309017 0 -0.95105702 0 0 -1 -0.309017 0 -0.951056 -0.309017 0 -0.951056 0 0 -1
		 -0.309017 0 -0.951056 -0.58778501 0 -0.809017 -0.58778501 0 -0.809017 -0.309017 0
		 -0.951056 -0.58778501 0 -0.809017 -0.809017 0 -0.58778501 -0.809017 0 -0.58778501
		 -0.58778501 0 -0.809017 -0.809017 0 -0.58778501 -0.95105702 0 -0.309017 -0.95105702
		 0 -0.309017 -0.809017 0 -0.58778501 -0.95105702 0 -0.309017 -1 0 0 -1 0 0 -0.95105702
		 0 -0.309017 -1 0 0 -0.951056 0 0.309017 -0.951056 0 0.309017 -1 0 0 -0.951056 0 0.309017
		 -0.809017 0 0.58778501 -0.809017 0 0.58778501 -0.951056 0 0.309017 -0.809017 0 0.58778501
		 -0.58778501 0 0.809017 -0.58778501 0 0.809017 -0.809017 0 0.58778501 -0.58778501
		 0 0.809017 -0.309017 0 0.95105702 -0.309017 0 0.95105702 -0.58778501 0 0.809017 -0.309017
		 0 0.95105702 0 0 1 0 0 1 -0.309017 0 0.95105702 0 0 1 0.309017 0 0.951056 0.309017
		 0 0.951056 0 0 1 0.309017 0 0.951056 0.58778501 0 0.809017 0.58778501 0 0.809017
		 0.309017 0 0.951056 0.58778501 0 0.809017 0.809017 0 0.58778501 0.809017 0 0.58778501
		 0.58778501 0 0.809017 0.809017 0 0.58778501 0.95105702 0 0.309017 0.95105702 0 0.309017
		 0.809017 0 0.58778501 0.95105702 0 0.309017 1 0 1e-006 1 0 1e-006 0.95105702 0 0.309017
		 1 0 1e-006 0.95105702 0 -0.30901599 0.95105702 0 -0.30901599 1 0 1e-006 0 -1 0 0
		 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0
		 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1
		 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0
		 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0
		 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1 0 0 -1
		 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0
		 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0;
	setAttr ".n[166:199]" -type "float3"  0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0
		 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0
		 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1 0 0 1
		 0;
	setAttr -s 60 -ch 200 ".fc[0:59]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 4 5 6 -2
		mu 0 4 1 4 5 2
		f 4 7 8 9 -6
		mu 0 4 6 7 8 9
		f 4 10 11 12 -9
		mu 0 4 7 10 11 8
		f 4 13 14 15 -12
		mu 0 4 10 12 13 11
		f 4 16 17 18 -15
		mu 0 4 12 14 15 13
		f 4 19 20 21 -18
		mu 0 4 16 17 18 19
		f 4 22 23 24 -21
		mu 0 4 17 20 21 18
		f 4 25 26 27 -24
		mu 0 4 20 22 23 21
		f 4 28 29 30 -27
		mu 0 4 22 24 25 23
		f 4 31 32 33 -30
		mu 0 4 24 26 27 25
		f 4 34 35 36 -33
		mu 0 4 26 28 29 27
		f 4 37 38 39 -36
		mu 0 4 30 31 32 33
		f 4 40 41 42 -39
		mu 0 4 31 34 35 32
		f 4 43 44 45 -42
		mu 0 4 34 36 37 35
		f 4 46 47 48 -45
		mu 0 4 36 38 39 37
		f 4 49 50 51 -48
		mu 0 4 40 41 42 43
		f 4 52 53 54 -51
		mu 0 4 41 44 45 42
		f 4 55 56 57 -54
		mu 0 4 44 46 47 45
		f 4 58 -4 59 -57
		mu 0 4 46 0 3 47
		f 3 -1 60 61
		mu 0 3 48 49 50
		f 3 -5 -62 62
		mu 0 3 51 48 50
		f 3 -8 -63 63
		mu 0 3 52 51 50
		f 3 -11 -64 64
		mu 0 3 53 52 50
		f 3 -14 -65 65
		mu 0 3 54 53 50
		f 3 -17 -66 66
		mu 0 3 55 54 50
		f 3 -20 -67 67
		mu 0 3 56 55 50
		f 3 -23 -68 68
		mu 0 3 57 56 50
		f 3 -26 -69 69
		mu 0 3 58 57 50
		f 3 -29 -70 70
		mu 0 3 59 58 50
		f 3 -32 -71 71
		mu 0 3 60 59 50
		f 3 -35 -72 72
		mu 0 3 61 60 50
		f 3 -38 -73 73
		mu 0 3 62 61 50
		f 3 -41 -74 74
		mu 0 3 63 62 50
		f 3 -44 -75 75
		mu 0 3 64 63 50
		f 3 -47 -76 76
		mu 0 3 65 64 50
		f 3 -50 -77 77
		mu 0 3 66 65 50
		f 3 -53 -78 78
		mu 0 3 67 66 50
		f 3 -56 -79 79
		mu 0 3 68 67 50
		f 3 -59 -80 -61
		mu 0 3 49 68 50
		f 3 -3 80 81
		mu 0 3 69 70 71
		f 3 -7 82 -81
		mu 0 3 70 72 71
		f 3 -10 83 -83
		mu 0 3 72 73 71
		f 3 -13 84 -84
		mu 0 3 73 74 71
		f 3 -16 85 -85
		mu 0 3 74 75 71
		f 3 -19 86 -86
		mu 0 3 75 76 71
		f 3 -22 87 -87
		mu 0 3 76 77 71
		f 3 -25 88 -88
		mu 0 3 77 78 71
		f 3 -28 89 -89
		mu 0 3 78 79 71
		f 3 -31 90 -90
		mu 0 3 79 80 71
		f 3 -34 91 -91
		mu 0 3 80 81 71
		f 3 -37 92 -92
		mu 0 3 81 82 71
		f 3 -40 93 -93
		mu 0 3 82 83 71
		f 3 -43 94 -94
		mu 0 3 83 84 71
		f 3 -46 95 -95
		mu 0 3 84 85 71
		f 3 -49 96 -96
		mu 0 3 85 86 71
		f 3 -52 97 -97
		mu 0 3 86 87 71
		f 3 -55 98 -98
		mu 0 3 87 88 71
		f 3 -58 99 -99
		mu 0 3 88 89 71
		f 3 -60 -82 -100
		mu 0 3 89 69 71;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
createNode transform -n "bundle5_BND";
	rename -uid "D44EFF6F-447D-FC51-B15D-428CAF4095C7";
	setAttr ".t" -type "double3" -6.7818632125854492 2.7105462551116943 -3.1993427276611328 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle5_BNDShape" -p "bundle5_BND";
	rename -uid "F3649C7D-4186-31B0-A82D-E69628370B61";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle6_BND";
	rename -uid "B05D1B05-4FE1-A132-A429-8A9C3EBC6818";
	setAttr ".t" -type "double3" -3.8366832733154297 2.9673919677734375 9.8209295272827148 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle6_BNDShape" -p "bundle6_BND";
	rename -uid "4CC926A1-4293-4650-52B8-48848211D95B";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle7_BND";
	rename -uid "C560E9DA-47F8-63E9-24C6-FBB62AC45923";
	setAttr ".t" -type "double3" 7.0452456474304199 1.8121918439865112 8.9415254592895508 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle7_BNDShape" -p "bundle7_BND";
	rename -uid "CBE07C13-4132-E5BB-69E6-88919A5E5F86";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle8_BND";
	rename -uid "A714F915-4F35-AD1D-2C7D-3DAF6E129BB6";
	setAttr ".t" -type "double3" 5.7129416465759277 1.7923740148544312 4.9636344909667969 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle8_BNDShape" -p "bundle8_BND";
	rename -uid "833C9A15-4D68-5DE4-37B3-A1BE7AB75234";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle9_BND";
	rename -uid "BADEBAAD-4B7D-FD88-1FCE-D3985B308051";
	setAttr ".t" -type "double3" 4.8134603500366211 2.5167403221130371 -2.0645403861999512 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle9_BNDShape" -p "bundle9_BND";
	rename -uid "B84CFFBF-485C-E627-C3B6-FBAF1A70864F";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle10_BND";
	rename -uid "7741851D-4E66-06CC-506C-309BDF40DE27";
	setAttr ".t" -type "double3" 4.208722761112913 5.1130008931975484 -5.3070131148552466 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle10_BNDShape" -p "bundle10_BND";
	rename -uid "BC65ABB2-467E-E9DF-1DEA-038B57355421";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle11_BND";
	rename -uid "EC62A1B7-4BA8-4BB3-9567-EC9A257BDC71";
	setAttr ".t" -type "double3" 0.0020688856020569801 0 7.1973309516906738 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle11_BNDShape" -p "bundle11_BND";
	rename -uid "DC73D265-4D82-A8D7-25ED-F2B2D37B9587";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle12_BND";
	rename -uid "E7419CC0-4E64-026F-2611-DDA5DED60E3E";
	setAttr ".t" -type "double3" 9.5971975326538086 0 -2.4054911136627197 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle12_BNDShape" -p "bundle12_BND";
	rename -uid "3A4781CC-44EC-28FD-700D-60B5A0015497";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "geom:pCube1";
	rename -uid "822BB177-4C56-2212-864E-CCA6D175C90C";
	setAttr ".rp" -type "double3" -20.425625801086426 11.580055475234985 12.339745998382568 ;
	setAttr ".sp" -type "double3" -20.425625801086426 11.580055475234985 12.339745998382568 ;
createNode mesh -n "geom:pCube1Shape" -p "geom:pCube1";
	rename -uid "C74A7C98-44E0-5CD6-AE53-19A849582D48";
	setAttr -k off ".v";
	setAttr ".iog[0].og[0].gcl" -type "componentList" 1 "f[0:5]";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 14 ".uvst[0].uvsp[0:13]" -type "float2" 0.375 0 0.625 0 0.625
		 0.25 0.375 0.25 0.625 0.5 0.375 0.5 0.625 0.75 0.375 0.75 0.625 1 0.375 1 0.875 0
		 0.875 0.25 0.125 0 0.125 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 8 ".vt[0:7]"  -23.42664719 7.49513578 14.45258045 -22.5429554 6.53700113 11.84853935
		 -16.39624023 14.85293293 14.13113976 -15.51254845 13.89479828 11.5270977 -18.3082962 16.62310982 12.8309536
		 -17.42460442 15.66497517 10.22691154 -25.33870316 9.26531315 13.15239429 -24.45501137 8.30717754 10.54835224;
	setAttr -s 12 ".ed[0:11]"  0 1 0 1 3 0 3 2 0 2 0 0 3 5 0 5 4 0 4 2 0
		 5 7 0 7 6 0 6 4 0 7 1 0 0 6 0;
	setAttr -s 24 ".n[0:23]" -type "float3"  1e+020 1e+020 1e+020 1e+020
		 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 1e+020 0.690494 0.72264898 -0.031569999
		 0.690494 0.72264898 -0.031569999 0.690494 0.72264898 -0.031569999 0.690494 0.72264898
		 -0.031569999 -0.65660399 0.60788202 -0.44648701 -0.65660399 0.60788202 -0.44648701
		 -0.65660399 0.60788202 -0.44648701 -0.65660399 0.60788202 -0.44648701 -0.690494 -0.72264898
		 0.031569999 -0.690494 -0.72264898 0.031569999 -0.690494 -0.72264898 0.031569999 -0.690494
		 -0.72264898 0.031569999 0.303462 -0.32902601 -0.89423299 0.303462 -0.32902601 -0.89423299
		 0.303462 -0.32902601 -0.89423299 0.303462 -0.32902601 -0.89423299 -0.303462 0.32902601
		 0.89423299 -0.303462 0.32902601 0.89423299 -0.303462 0.32902601 0.89423299 -0.303462
		 0.32902601 0.89423299;
	setAttr -s 6 -ch 24 ".fc[0:5]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 -3 4 5 6
		mu 0 4 3 2 4 5
		f 4 -6 7 8 9
		mu 0 4 5 4 6 7
		f 4 -9 10 -1 11
		mu 0 4 7 6 8 9
		f 4 -11 -8 -5 -2
		mu 0 4 1 10 11 2
		f 4 -12 -4 -7 -10
		mu 0 4 12 0 3 13;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
createNode transform -n "bundle3_BND" -p "geom:pCube1";
	rename -uid "84192200-461C-EDFA-9B80-2A95EDE57637";
	setAttr ".t" -type "double3" -19.469621658325195 10.694968223571777 12.989875793457031 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle3_BNDShape" -p "bundle3_BND";
	rename -uid "D2B456EA-4ECD-833F-3315-29ABBE5B77B4";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle4_BND" -p "geom:pCube1";
	rename -uid "EB5D3E4F-461D-6766-9B75-18B61B192A26";
	setAttr ".t" -type "double3" -15.954599380493164 14.374087333679199 12.829724311828613 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle4_BNDShape" -p "bundle4_BND";
	rename -uid "7370BF79-4ED9-78FA-6ACB-8A8FB3D233F2";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle2_BND" -p "geom:pCube1";
	rename -uid "9640BB85-46EF-F291-0350-15804C1CCF54";
	setAttr ".t" -type "double3" -16.91180419921875 15.260347366333008 12.180685997009277 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle2_BNDShape" -p "bundle2_BND";
	rename -uid "B332FCB7-4A11-201F-E8EF-4782D0202B60";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode transform -n "bundle1_BND" -p "geom:pCube1";
	rename -uid "7526574E-4B85-AFD6-B3C5-C5AAA1E56EA6";
	setAttr ".t" -type "double3" -20.867494583129883 12.059128761291504 13.641757011413574 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode locator -n "bundle1_BNDShape" -p "bundle1_BND";
	rename -uid "14D9D5FB-48D8-DD68-2E91-FEBFAC4B3BA8";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.1 0.1 0.1 ;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "0D4E6B08-43C6-85D2-B78D-6C85B21BE40F";
	setAttr -s 10 ".lnk";
	setAttr -s 10 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "D6C02477-4B19-EE9C-8A4D-2C858FDC92BB";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "703B4F10-41C1-4206-FA7B-18A782D219DC";
createNode displayLayerManager -n "layerManager";
	rename -uid "0A066157-40F6-D02C-31E6-FBAB9625D494";
createNode displayLayer -n "defaultLayer";
	rename -uid "90B9F90B-4320-12F2-E701-098B3586F981";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "F7077895-43D0-2F98-F59D-5B8D1D3DDB0F";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "08FA9545-46C6-896C-1B38-6D86530C5B7C";
	setAttr ".g" yes;
createNode script -n "mmSolver_data_node";
	rename -uid "37770258-4697-1D29-93B2-51BE9872C813";
	addAttr -ci true -sn "mmSolver_data" -ln "mmSolver_data" -dt "string";
	setAttr -l on ".mmSolver_data" -type "string" "{\"active_collection_uid\": \"89BFF4AE-454C-6075-6D49-E59BE1C6385A\"}";
createNode lambert -n "lambert2";
	rename -uid "6F55210C-4BD8-C9D4-2F4D-45A16B558229";
createNode shadingEngine -n "lambert2SG";
	rename -uid "708CA592-47C5-F1FE-45C7-5BB9CF3F25CD";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo1";
	rename -uid "8CF4AE67-450E-B826-58D0-409099C617BA";
createNode checker -n "checker1";
	rename -uid "C7FD1C49-43C7-55F2-8FCF-379B68977706";
	setAttr ".c2" -type "float3" 1 0 0 ;
createNode place2dTexture -n "place2dTexture1";
	rename -uid "6BE782E9-417D-4F14-2398-FCAB96A11E77";
	setAttr ".re" -type "float2" 10 7.5 ;
createNode lambert -n "lambert3";
	rename -uid "3C95D9B7-46DB-EB7E-D52C-439889A82A09";
createNode shadingEngine -n "lambert3SG";
	rename -uid "C45C68F0-42EC-8EA1-D12F-7B805988E99F";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo2";
	rename -uid "61DDA6F0-4D89-8827-AF2A-B5B3BA5C062F";
createNode checker -n "checker2";
	rename -uid "460127C8-42B7-3E9C-2634-45ABBA265195";
createNode place2dTexture -n "place2dTexture2";
	rename -uid "E27DF1A7-46A6-CAF2-A22E-9FBAD60BCBA4";
	setAttr ".re" -type "float2" 4 4 ;
createNode lambert -n "lambert4";
	rename -uid "5E163D61-4E4E-64EA-5722-06AB56320254";
createNode shadingEngine -n "lambert4SG";
	rename -uid "2BF7A827-4A88-BEE4-2EF2-6B837F5BA595";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo3";
	rename -uid "7905E67C-45DB-9B98-DE42-4EA610FE2DEC";
createNode checker -n "checker3";
	rename -uid "DFD520FD-4C1E-4543-89BA-9E84AA0FF2F1";
	setAttr ".c2" -type "float3" 0 0 1 ;
createNode place2dTexture -n "place2dTexture3";
	rename -uid "20880D03-4990-E23E-D401-A7BE1D6D14B3";
	setAttr ".re" -type "float2" 4 4 ;
createNode lambert -n "lambert5";
	rename -uid "EA3E7EDE-457C-0195-2275-3C878544A918";
createNode shadingEngine -n "lambert5SG";
	rename -uid "65048FC4-404D-C0F6-A233-7FAA7DE74572";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo4";
	rename -uid "3E8C5615-412E-9860-0EBD-18ACBC77BAD4";
createNode checker -n "checker4";
	rename -uid "78630131-4E98-A4E3-C7FF-17BF0EA53157";
	setAttr ".c2" -type "float3" 0 1 0 ;
createNode place2dTexture -n "place2dTexture4";
	rename -uid "4D9649C0-4380-3237-DC15-879DA124486C";
	setAttr ".re" -type "float2" 4 4 ;
createNode script -n "uiConfigurationScriptNode";
	rename -uid "438640A9-4752-C2A1-0DD7-57A40AC6F425";
	setAttr ".b" -type "string" (
		"// Maya Mel UI Configuration File.\n//\n//  This script is machine generated.  Edit at your own risk.\n//\n//\n\nglobal string $gMainPane;\nif (`paneLayout -exists $gMainPane`) {\n\n\tglobal int $gUseScenePanelConfig;\n\tint    $useSceneConfig = $gUseScenePanelConfig;\n\tint    $menusOkayInPanels = `optionVar -q allowMenusInPanels`;\tint    $nVisPanes = `paneLayout -q -nvp $gMainPane`;\n\tint    $nPanes = 0;\n\tstring $editorName;\n\tstring $panelName;\n\tstring $itemFilterName;\n\tstring $panelConfig;\n\n\t//\n\t//  get current state of the UI\n\t//\n\tsceneUIReplacement -update $gMainPane;\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"graphEditor\" (localizedPanelLabel(\"Graph Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"graphEditor\" -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n"
		+ "                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 1\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 1\n                -setFilter \"0\" \n                -showSetMembers 0\n"
		+ "                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n"
		+ "                -displayActiveKeyTangents 1\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 1\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -showResults \"off\" \n                -showBufferCurves \"off\" \n                -smoothness \"fine\" \n                -resultSamples 1\n                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -showCurveNames 0\n                -showActiveCurveNames 0\n                -stackedCurves 0\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -displayNormalized 1\n                -preSelectionHighlight 0\n                -constrainDrag 0\n                -classicMode 1\n                -valueLinesToggle 1\n                -outliner \"graphEditor1OutlineEd\" \n                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 1\n"
		+ "                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 1\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n"
		+ "\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 1\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 1\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -showResults \"off\" \n                -showBufferCurves \"off\" \n                -smoothness \"fine\" \n                -resultSamples 1\n                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -showCurveNames 0\n                -showActiveCurveNames 0\n                -stackedCurves 0\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -displayNormalized 1\n                -preSelectionHighlight 0\n                -constrainDrag 0\n                -classicMode 1\n                -valueLinesToggle 1\n"
		+ "                -outliner \"graphEditor1OutlineEd\" \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"scriptEditorPanel\" (localizedPanelLabel(\"Script Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"scriptEditorPanel\" -l (localizedPanelLabel(\"Script Editor\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Script Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Top View\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `modelPanel -unParent -l (localizedPanelLabel(\"Top View\")) -mbv $menusOkayInPanels `;\n\t\t\t$editorName = $panelName;\n            modelEditor -e \n                -camera \"top\" \n                -useInteractiveMode 0\n"
		+ "                -displayLights \"default\" \n                -displayAppearance \"smoothShaded\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -holdOuts 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 0\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 32768\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n"
		+ "                -depthOfFieldPreview 1\n                -maxConstantTransparency 1\n                -rendererName \"vp2Renderer\" \n                -objectFilterShowInHUD 1\n                -isFiltered 0\n                -colorResolution 256 256 \n                -bumpResolution 512 512 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 1\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n"
		+ "                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -imagePlane 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -clipGhosts 1\n                -greasePencils 1\n                -shadows 0\n                -captureSequenceNumber -1\n                -width 1\n                -height 1\n                -sceneRenderFilter 0\n                $editorName;\n"
		+ "            modelEditor -e -viewSelected 0 $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Top View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"top\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n"
		+ "            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n"
		+ "            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Side View\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `modelPanel -unParent -l (localizedPanelLabel(\"Side View\")) -mbv $menusOkayInPanels `;\n\t\t\t$editorName = $panelName;\n            modelEditor -e \n                -camera \"side\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"smoothShaded\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -holdOuts 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 0\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n"
		+ "                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 32768\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -depthOfFieldPreview 1\n                -maxConstantTransparency 1\n                -rendererName \"vp2Renderer\" \n                -objectFilterShowInHUD 1\n                -isFiltered 0\n                -colorResolution 256 256 \n                -bumpResolution 512 512 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 1\n                -occlusionCulling 0\n                -shadingModel 0\n"
		+ "                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -imagePlane 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n"
		+ "                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -clipGhosts 1\n                -greasePencils 1\n                -shadows 0\n                -captureSequenceNumber -1\n                -width 1\n                -height 1\n                -sceneRenderFilter 0\n                $editorName;\n            modelEditor -e -viewSelected 0 $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Side View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"side\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n"
		+ "            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n"
		+ "            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n"
		+ "            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Front View\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `modelPanel -unParent -l (localizedPanelLabel(\"Front View\")) -mbv $menusOkayInPanels `;\n\t\t\t$editorName = $panelName;\n            modelEditor -e \n                -camera \"front\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"smoothShaded\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n"
		+ "                -headsUpDisplay 1\n                -holdOuts 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 0\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 32768\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -depthOfFieldPreview 1\n                -maxConstantTransparency 1\n                -rendererName \"vp2Renderer\" \n                -objectFilterShowInHUD 1\n"
		+ "                -isFiltered 0\n                -colorResolution 256 256 \n                -bumpResolution 512 512 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 1\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -imagePlane 1\n"
		+ "                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -clipGhosts 1\n                -greasePencils 1\n                -shadows 0\n                -captureSequenceNumber -1\n                -width 1\n                -height 1\n                -sceneRenderFilter 0\n                $editorName;\n            modelEditor -e -viewSelected 0 $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Front View\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"front\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n"
		+ "            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n"
		+ "            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Persp View\")) `;\n\tif (\"\" == $panelName) {\n"
		+ "\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `modelPanel -unParent -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels `;\n\t\t\t$editorName = $panelName;\n            modelEditor -e \n                -camera \"cameraShape1\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"wireframe\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -holdOuts 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 0\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n"
		+ "                -textureMaxSize 32768\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -depthOfFieldPreview 1\n                -maxConstantTransparency 1\n                -rendererName \"vp2Renderer\" \n                -objectFilterShowInHUD 1\n                -isFiltered 0\n                -colorResolution 256 256 \n                -bumpResolution 512 512 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 1\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n"
		+ "                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -imagePlane 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n"
		+ "                -motionTrails 1\n                -clipGhosts 1\n                -greasePencils 1\n                -shadows 0\n                -captureSequenceNumber -1\n                -width 1276\n                -height 1412\n                -sceneRenderFilter 0\n                $editorName;\n            modelEditor -e -viewSelected 0 $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"cameraShape1\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"wireframe\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n"
		+ "            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n"
		+ "            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n"
		+ "            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1276\n            -height 1412\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"ToggledOutliner\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `outlinerPanel -unParent -l (localizedPanelLabel(\"ToggledOutliner\")) -mbv $menusOkayInPanels `;\n\t\t\t$editorName = $panelName;\n            outlinerEditor -e \n                -showShapes 0\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 0\n                -showConnected 0\n                -showAnimCurvesOnly 0\n                -showMuteInfo 0\n"
		+ "                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 0\n                -showDagOnly 1\n                -showAssets 1\n                -showContainedOnly 1\n                -showPublishedAsConnected 0\n                -showContainerContents 1\n                -ignoreDagHierarchy 0\n                -expandConnections 0\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 1\n                -showLeafs 1\n                -showNumericAttrsOnly 0\n                -highlightActive 1\n                -autoSelectNewObjects 0\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 0\n                -setFilter \"defaultSetFilter\" \n                -showSetMembers 1\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -isSet 0\n                -isSetMember 0\n                -displayMode \"DAG\" \n"
		+ "                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 0\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                -renderFilterIndex 0\n                -selectionOrder \"chronological\" \n                -expandAttribute 0\n                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"ToggledOutliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n"
		+ "        outlinerEditor -e \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 0\n            -showReferenceMembers 0\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n"
		+ "            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -isSet 0\n            -isSetMember 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            -renderFilterIndex 0\n            -selectionOrder \"chronological\" \n            -expandAttribute 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n"
		+ "\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"Outliner\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `outlinerPanel -unParent -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels `;\n\t\t\t$editorName = $panelName;\n            outlinerEditor -e \n                -showShapes 0\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 0\n                -showConnected 0\n                -showAnimCurvesOnly 0\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 0\n                -showDagOnly 1\n                -showAssets 1\n                -showContainedOnly 1\n                -showPublishedAsConnected 0\n                -showContainerContents 1\n                -ignoreDagHierarchy 0\n                -expandConnections 0\n"
		+ "                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 1\n                -showLeafs 1\n                -showNumericAttrsOnly 0\n                -highlightActive 1\n                -autoSelectNewObjects 0\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 0\n                -setFilter \"defaultSetFilter\" \n                -showSetMembers 1\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n"
		+ "                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 0\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 0\n            -showReferenceMembers 0\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showContainerContents 1\n"
		+ "            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -showNamespace 1\n"
		+ "            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dopeSheetPanel\" (localizedPanelLabel(\"Dope Sheet\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"dopeSheetPanel\" -l (localizedPanelLabel(\"Dope Sheet\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n"
		+ "                -autoExpand 0\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 0\n                -showCompounds 1\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 0\n                -doNotSelectNewObjects 1\n                -dropIsParent 1\n                -transmitFilters 0\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n"
		+ "                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"DopeSheetEd\");\n            dopeSheetEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -outliner \"dopeSheetPanel1OutlineEd\" \n                -showSummary 1\n"
		+ "                -showScene 0\n                -hierarchyBelow 0\n                -showTicks 1\n                -selectionWindow 0 0 0 0 \n                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dope Sheet\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 0\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showContainerContents 0\n"
		+ "                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 0\n                -showCompounds 1\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 0\n                -doNotSelectNewObjects 1\n                -dropIsParent 1\n                -transmitFilters 0\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n"
		+ "                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"DopeSheetEd\");\n            dopeSheetEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -outliner \"dopeSheetPanel1OutlineEd\" \n                -showSummary 1\n                -showScene 0\n                -hierarchyBelow 0\n                -showTicks 1\n                -selectionWindow 0 0 0 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n"
		+ "\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"timeEditorPanel\" (localizedPanelLabel(\"Time Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"timeEditorPanel\" -l (localizedPanelLabel(\"Time Editor\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Time Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"clipEditorPanel\" (localizedPanelLabel(\"Trax Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"clipEditorPanel\" -l (localizedPanelLabel(\"Trax Editor\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = clipEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n"
		+ "                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 0 \n                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Trax Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = clipEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"sequenceEditorPanel\" (localizedPanelLabel(\"Camera Sequencer\")) `;\n"
		+ "\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"sequenceEditorPanel\" -l (localizedPanelLabel(\"Camera Sequencer\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = sequenceEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 1 \n                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Camera Sequencer\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = sequenceEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n"
		+ "                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 1 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperGraphPanel\" (localizedPanelLabel(\"Hypergraph Hierarchy\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"hyperGraphPanel\" -l (localizedPanelLabel(\"Hypergraph Hierarchy\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"HyperGraphEd\");\n            hyperGraph -e \n                -graphLayoutStyle \"hierarchicalLayout\" \n                -orientation \"horiz\" \n                -mergeConnections 0\n                -zoom 1\n                -animateTransition 0\n                -showRelationships 1\n                -showShapes 0\n                -showDeformers 0\n"
		+ "                -showExpressions 0\n                -showConstraints 0\n                -showConnectionFromSelected 0\n                -showConnectionToSelected 0\n                -showConstraintLabels 0\n                -showUnderworld 0\n                -showInvisible 0\n                -transitionFrames 1\n                -opaqueContainers 0\n                -freeform 0\n                -imagePosition 0 0 \n                -imageScale 1\n                -imageEnabled 0\n                -graphType \"DAG\" \n                -heatMapDisplay 0\n                -updateSelection 1\n                -updateNodeAdded 1\n                -useDrawOverrideColor 0\n                -limitGraphTraversal -1\n                -range 0 0 \n                -iconSize \"smallIcons\" \n                -showCachedConnections 0\n                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypergraph Hierarchy\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"HyperGraphEd\");\n"
		+ "            hyperGraph -e \n                -graphLayoutStyle \"hierarchicalLayout\" \n                -orientation \"horiz\" \n                -mergeConnections 0\n                -zoom 1\n                -animateTransition 0\n                -showRelationships 1\n                -showShapes 0\n                -showDeformers 0\n                -showExpressions 0\n                -showConstraints 0\n                -showConnectionFromSelected 0\n                -showConnectionToSelected 0\n                -showConstraintLabels 0\n                -showUnderworld 0\n                -showInvisible 0\n                -transitionFrames 1\n                -opaqueContainers 0\n                -freeform 0\n                -imagePosition 0 0 \n                -imageScale 1\n                -imageEnabled 0\n                -graphType \"DAG\" \n                -heatMapDisplay 0\n                -updateSelection 1\n                -updateNodeAdded 1\n                -useDrawOverrideColor 0\n                -limitGraphTraversal -1\n                -range 0 0 \n"
		+ "                -iconSize \"smallIcons\" \n                -showCachedConnections 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"visorPanel\" (localizedPanelLabel(\"Visor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"visorPanel\" -l (localizedPanelLabel(\"Visor\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Visor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"createNodePanel\" (localizedPanelLabel(\"Create Node\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"createNodePanel\" -l (localizedPanelLabel(\"Create Node\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Create Node\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"polyTexturePlacementPanel\" (localizedPanelLabel(\"UV Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"polyTexturePlacementPanel\" -l (localizedPanelLabel(\"UV Editor\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"UV Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"renderWindowPanel\" (localizedPanelLabel(\"Render View\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"renderWindowPanel\" -l (localizedPanelLabel(\"Render View\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Render View\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"shapePanel\" (localizedPanelLabel(\"Shape Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\tshapePanel -unParent -l (localizedPanelLabel(\"Shape Editor\")) -mbv $menusOkayInPanels ;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tshapePanel -edit -l (localizedPanelLabel(\"Shape Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"posePanel\" (localizedPanelLabel(\"Pose Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\tposePanel -unParent -l (localizedPanelLabel(\"Pose Editor\")) -mbv $menusOkayInPanels ;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tposePanel -edit -l (localizedPanelLabel(\"Pose Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynRelEdPanel\" (localizedPanelLabel(\"Dynamic Relationships\")) `;\n"
		+ "\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"dynRelEdPanel\" -l (localizedPanelLabel(\"Dynamic Relationships\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dynamic Relationships\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"relationshipPanel\" (localizedPanelLabel(\"Relationship Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"relationshipPanel\" -l (localizedPanelLabel(\"Relationship Editor\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Relationship Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"referenceEditorPanel\" (localizedPanelLabel(\"Reference Editor\")) `;\n"
		+ "\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"referenceEditorPanel\" -l (localizedPanelLabel(\"Reference Editor\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Reference Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"componentEditorPanel\" (localizedPanelLabel(\"Component Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"componentEditorPanel\" -l (localizedPanelLabel(\"Component Editor\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Component Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynPaintScriptedPanelType\" (localizedPanelLabel(\"Paint Effects\")) `;\n"
		+ "\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"dynPaintScriptedPanelType\" -l (localizedPanelLabel(\"Paint Effects\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Paint Effects\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"profilerPanel\" (localizedPanelLabel(\"Profiler Tool\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"profilerPanel\" -l (localizedPanelLabel(\"Profiler Tool\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Profiler Tool\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"contentBrowserPanel\" (localizedPanelLabel(\"Content Browser\")) `;\n"
		+ "\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"contentBrowserPanel\" -l (localizedPanelLabel(\"Content Browser\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Content Browser\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"Stereo\" (localizedPanelLabel(\"Stereo\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"Stereo\" -l (localizedPanelLabel(\"Stereo\")) -mbv $menusOkayInPanels `;\nstring $editorName = ($panelName+\"Editor\");\n            stereoCameraView -e \n                -camera \"cameraShape1\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"wireframe\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n"
		+ "                -headsUpDisplay 1\n                -holdOuts 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 1\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 32768\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -depthOfFieldPreview 1\n                -maxConstantTransparency 1\n                -objectFilterShowInHUD 1\n                -isFiltered 0\n                -colorResolution 4 4 \n"
		+ "                -bumpResolution 4 4 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 0\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -imagePlane 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n"
		+ "                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -clipGhosts 1\n                -greasePencils 1\n                -shadows 0\n                -captureSequenceNumber -1\n                -width 0\n                -height 0\n                -sceneRenderFilter 0\n                -displayMode \"centerEye\" \n                -viewColor 0 0 0 1 \n                -useCustomBackground 1\n                $editorName;\n            stereoCameraView -e -viewSelected 0 $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Stereo\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "string $editorName = ($panelName+\"Editor\");\n            stereoCameraView -e \n                -camera \"cameraShape1\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"wireframe\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -holdOuts 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 1\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 32768\n                -fogging 0\n                -fogSource \"fragment\" \n"
		+ "                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -depthOfFieldPreview 1\n                -maxConstantTransparency 1\n                -objectFilterShowInHUD 1\n                -isFiltered 0\n                -colorResolution 4 4 \n                -bumpResolution 4 4 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 0\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n"
		+ "                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -imagePlane 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -clipGhosts 1\n                -greasePencils 1\n                -shadows 0\n                -captureSequenceNumber -1\n                -width 0\n"
		+ "                -height 0\n                -sceneRenderFilter 0\n                -displayMode \"centerEye\" \n                -viewColor 0 0 0 1 \n                -useCustomBackground 1\n                $editorName;\n            stereoCameraView -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperShadePanel\" (localizedPanelLabel(\"Hypershade\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"hyperShadePanel\" -l (localizedPanelLabel(\"Hypershade\")) -mbv $menusOkayInPanels `;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypershade\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"nodeEditorPanel\" (localizedPanelLabel(\"Node Editor\")) `;\n\tif (\"\" == $panelName) {\n\t\tif ($useSceneConfig) {\n\t\t\t$panelName = `scriptedPanel -unParent  -type \"nodeEditorPanel\" -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels `;\n"
		+ "\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -defaultPinnedState 0\n                -additiveGraphingMode 0\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                -activeTab -1\n                -editorMode \"default\" \n                $editorName;\n\t\t}\n\t} else {\n\t\t$label = `panel -q -label $panelName`;\n"
		+ "\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -defaultPinnedState 0\n                -additiveGraphingMode 0\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                -activeTab -1\n                -editorMode \"default\" \n"
		+ "                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\tif ($useSceneConfig) {\n        string $configName = `getPanel -cwl (localizedPanelLabel(\"Current Layout\"))`;\n        if (\"\" != $configName) {\n\t\t\tpanelConfiguration -edit -label (localizedPanelLabel(\"Current Layout\")) \n\t\t\t\t-userCreated false\n\t\t\t\t-defaultImage \"vacantCell.xP:/\"\n\t\t\t\t-image \"\"\n\t\t\t\t-sc false\n\t\t\t\t-configString \"global string $gMainPane; paneLayout -e -cn \\\"single\\\" -ps 1 100 100 $gMainPane;\"\n\t\t\t\t-removeAllPanels\n\t\t\t\t-ap false\n\t\t\t\t\t(localizedPanelLabel(\"Persp View\")) \n\t\t\t\t\t\"modelPanel\"\n"
		+ "\t\t\t\t\t\"$panelName = `modelPanel -unParent -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels `;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -camera \\\"cameraShape1\\\" \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"wireframe\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 32768\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1276\\n    -height 1412\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName\"\n"
		+ "\t\t\t\t\t\"modelPanel -edit -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels  $panelName;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -camera \\\"cameraShape1\\\" \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"wireframe\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 32768\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1276\\n    -height 1412\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName\"\n"
		+ "\t\t\t\t$configName;\n\n            setNamedPanelLayout (localizedPanelLabel(\"Current Layout\"));\n        }\n\n        panelHistory -e -clear mainPanelHistory;\n        setFocus `paneLayout -q -p1 $gMainPane`;\n        sceneUIReplacement -deleteRemaining;\n        sceneUIReplacement -clear;\n\t}\n\n\ngrid -spacing 5 -size 12 -divisions 5 -displayAxes yes -displayGridLines yes -displayDivisionLines yes -displayPerspectiveLabels no -displayOrthographicLabels no -displayAxesBold yes -perspectiveLabelPosition axis -orthographicLabelPosition edge;\nviewManip -drawCompass 0 -compassAngle 0 -frontParameters \"\" -homeParameters \"\" -selectionLockParameters \"\";\n}\n");
	setAttr ".st" 3;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "ADCFC8D5-4217-99E3-EF93-A88433C98238";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 120 -ast 1 -aet 200 ";
	setAttr ".st" 6;
createNode mmMarkerScale -n "mmMarkerScale1";
	rename -uid "756EC19F-4140-3763-B0ED-8EA010D2E82B";
createNode animCurveTL -n "pCube1_locator9_MKR_translateX";
	rename -uid "03506C58-4487-85B5-5A80-16A5C601FEFE";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 -0.32017183213138534 2 -0.32015081929340189
		 3 -0.32008824609699116 4 -0.31998479873916952 5 -0.31984114845319195 6 -0.31965795242764
		 7 -0.31943585471501063 8 -0.31917548712932986 9 -0.31887747013240136 10 -0.31854241370835079
		 11 -0.31817091822616617 12 -0.3177635752899744 13 -0.31732096857680631 14 -0.31684367466161245
		 15 -0.31633226382930058 16 -0.31578730087354379 17 -0.31520934588211474 18 -0.31459895500846169
		 19 -0.31395668122923837 20 -0.31328307508745534 21 -0.31257868542090722 22 -0.31184406007548737
		 23 -0.31107974660297277 24 -0.31028629294283372 25 -0.30946424808758449 26 -0.30861416273116415
		 27 -0.30773658989980457 28 -0.30683208556482333 29 -0.30590120923674269 30 -0.30494452454012438
		 31 -0.30396259976849399 32 -0.30295600841870829 33 -0.30192532970411667 34 -0.30087114904586382
		 35 -0.29979405854167984 36 -0.2986946574115153 37 -0.29757355241938938 38 -0.29643135827083333
		 39 -0.29526869798534616 40 -0.29408620324330048 41 -0.29288451470677096 42 -0.29166428231381086
		 43 -0.29042616554573308 44 -0.28917083366701646 45 -0.2878989659375108 46 -0.28661125179667407
		 47 -0.28530839101964556 48 -0.28399109384503052 49 -0.28266008107433838 50 -0.28131608414310583
		 51 -0.27995984516380751 52 -0.27859211694074532 53 -0.2772136629571918 54 -0.27582525733514646
		 55 -0.27442768476815388 56 -0.27302174042771815 57 -0.2716082298439389 58 -0.27018796876106882
		 59 -0.26876178296879333 60 -0.26733050811009862 61 -0.26589498946668549 62 -0.26445608172295393
		 63 -0.26301464870966257 64 -0.26157156312842467 65 -0.26012770625827764 66 -0.25868396764560786
		 67 -0.25724124477877447 68 -0.25580044274880909 69 -0.25436247389762384 70 -0.25292825745517
		 71 -0.2514987191670362 72 -0.25007479091397938 73 -0.24865741032488964 74 -0.24724752038470754
		 75 -0.24584606903878392 76 -0.24445400879518564 77 -0.24307229632640437 78 -0.24170189207191722
		 79 -0.24034375984299844 80 -0.23899886643114598 81 -0.2376681812214323 82 -0.2363526758120339
		 83 -0.2350533236411263 84 -0.23377109962226506 85 -0.23250697978929064 86 -0.23126194095172065
		 87 -0.23003696036149923 88 -0.22883301539187617 89 -0.22765108322910443 90 -0.22649214057752753
		 91 -0.22535716337852985 92 -0.22424712654371426 93 -0.2231630037025516 94 -0.22210576696463868
		 95 -0.22107638669657304 96 -0.22007583131334452 97 -0.21910506708400401 98 -0.21816505795126062
		 99 -0.21725676536452021 100 -0.21638114812575415 101 -0.21553916224746017 102 -0.21473176082184031
		 103 -0.21395989390019132 104 -0.21322450838137536 105 -0.21252654790809333 106 -0.21186695276955814
		 107 -0.21124665980902158 108 -0.21066660233447571 109 -0.2101277100307074 110 -0.20963090887074415
		 111 -0.20917712102458896 112 -0.20876726476299767 113 -0.20840225435390369 114 -0.2080829999489523
		 115 -0.20781040745745377 116 -0.20758537840491331 117 -0.20740880977314369 118 -0.20728159381880651
		 119 -0.20720461786708055 120 -0.20717876407697988;
createNode animCurveTL -n "pCube1_locator9_MKR_translateY";
	rename -uid "4FA8C536-4F3A-7F05-6595-3998C0DFE6AC";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 0.2784736709916098 2 0.27848599576186328
		 3 0.27852269456009715 4 0.2785833572956764 5 0.27866757786561969 6 0.27877495381893991
		 7 0.2789050859968536 8 0.27905757815312948 9 0.27923203655866935 10 0.2794280695942104
		 11 0.27964528733484473 12 0.2798833011298677 13 0.28014172318127817 14 0.28042016612407705
		 15 0.28071824261132328 16 0.28103556490673931 17 0.28137174448747926 18 0.28172639165950253
		 19 0.28209911518782715 20 0.28248952194376709 21 0.28289721657110123 22 0.28332180117293171
		 23 0.2837628750208645 24 0.2842200342879404 25 0.28469287180661262 26 0.28518097685288679
		 27 0.28568393495759259 28 0.28620132774557661 29 0.28673273280347211 30 0.28727772357651427
		 31 0.28783586929473159 32 0.28840673492868407 33 0.28898988117475533 34 0.28958486446986198
		 35 0.29019123703529526 36 0.29080854694924652 37 0.29143633824745097 38 0.29207415105121493
		 39 0.29272152172198007 40 0.2933779830414307 41 0.29404306441603567 42 0.29471629210479322
		 43 0.29539718946883053 44 0.29608527724141576 45 0.29678007381682936 46 0.29748109555646296
		 47 0.2981878571104295 48 0.29889987175289301 49 0.29961665172927621 50 0.30033770861344145
		 51 0.30106255367290213 52 0.30179069824009952 53 0.30252165408774889 54 0.30325493380625845
		 55 0.30399005118121636 56 0.30472652156897917 57 0.30546386226838218 58 0.3062015928866636
		 59 0.30693923569771497 60 0.30767631599084289 61 0.30841236240827841 62 0.30914690726975902
		 63 0.3098794868825836 64 0.31060964183563422 65 0.31133691727596546 66 0.31206086316665282
		 67 0.31278103452472639 68 0.31349699163811251 69 0.31420830026064461 70 0.31491453178431883
		 71 0.31561526338810786 72 0.31631007816276757 73 0.31699856521120751 74 0.31768031972412836
		 75 0.31835494303074641 76 0.31902204262457134 77 0.31968123216430533 78 0.32033213145007222
		 79 0.32097436637528343 80 0.32160756885456498 81 0.32223137672827318 82 0.32284543364421503
		 83 0.32344938891728636 84 0.32404289736781222 85 0.32462561913944832 86 0.32519721949756186
		 87 0.32575736860906401 88 0.32630574130470402 89 0.32684201682486858 90 0.32736587854994892
		 91 0.32787701371635614 92 0.32837511311925494 93 0.32885987080308055 94 0.32933098374089398
		 95 0.32978815150358565 96 0.33023107591991185 97 0.33065946072829933 98 0.33107301122129429
		 99 0.33147143388347888 100 0.33185443602360154 101 0.33222172540160166 102 0.33257300985111993
		 103 0.33290799689801809 104 0.33322639337532722 105 0.33352790503497265 106 0.33381223615652433
		 107 0.33407908915314244 108 0.33432816417479216 109 0.33455915870872732 110 0.33477176717716417
		 111 0.33496568053198772 112 0.33514058584627848 113 0.3352961659023872 114 0.33543209877624758
		 115 0.33554805741758176 116 0.33564370922564257 117 0.33571871562014399 118 0.33577273160704246
		 119 0.3358054053388938 120 0.33581637766955863;
createNode animCurveTU -n "pCube1_locator9_MKR_enable";
	rename -uid "4827AA6E-4641-86B3-34B9-A0AEC7FAD352";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 122 ".ktv[0:121]"  0 0 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1
		 95 1 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1
		 110 1 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1 121 0;
createNode animCurveTU -n "pCube1_locator9_MKR_weight";
	rename -uid "B63FEE14-4DF1-1A38-65A2-88BEC64F3309";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1 10 1
		 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1 27 1
		 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1 44 1
		 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1 61 1
		 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1
		 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1 95 1
		 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1 110 1
		 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1;
createNode animCurveTL -n "pCube1_locator10_MKR_translateX";
	rename -uid "29C5C350-4913-2F25-01D1-35B04F6F7798";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 -0.27366988229885153 2 -0.27363841256899279
		 3 -0.27354470696775901 4 -0.27338981292717068 5 -0.2731747679528389 6 -0.27290060055056653
		 7 -0.2725683312405815 8 -0.2721789736449729 9 -0.27173353563461494 10 -0.27123302052252046
		 11 -0.27067842829119043 12 -0.27007075684212062 13 -0.26941100325618184 14 -0.2687001650541137
		 15 -0.26793924144688913 16 -0.26712923456617804 17 -0.26627115066562801 18 -0.26536600128412813
		 19 -0.26441480436269493 20 -0.26341858530706835 21 -0.26237837798858465 22 -0.26129522567635693
		 23 -0.26017018189428914 24 -0.25900431119695383 25 -0.25779868985888571 26 -0.25655440647238986
		 27 -0.25527256244952778 28 -0.25395427242454383 29 -0.25260066455359337 30 -0.25121288070928355
		 31 -0.24979207656819136 32 -0.24833942159019523 33 -0.24685609888915616 34 -0.2453433049951857
		 35 -0.24380224950945761 36 -0.24223415465323345 37 -0.24064025471350037 38 -0.23902179538832163
		 39 -0.23738003303571309 40 -0.23571623383053764 41 -0.23403167283456383 42 -0.23232763298548065
		 43 -0.23060540401123586 44 -0.22886628127662884 45 -0.22711156456958753 46 -0.2253425568350047
		 47 -0.22356056286440557 48 -0.22176688795003952 49 -0.21996283651224657 50 -0.21814971070914413
		 51 -0.21632880903778406 52 -0.21450142493597957 53 -0.21266884539395731 54 -0.21083234958487973
		 55 -0.20899320752309714 56 -0.20715267875872267 57 -0.20531201111679948 58 -0.20347243948891702
		 59 -0.20163518468468633 60 -0.19980145234994906 61 -0.19797243195803271 62 -0.19614929587973767
		 63 -0.19433319853708858 64 -0.19252527564518385 65 -0.19072664354577129 66 -0.18893839863543727
		 67 -0.18716161689055655 68 -0.18539735349040698 69 -0.18364664253911867 70 -0.18191049688639693
		 71 -0.18018990804626245 72 -0.17848584621237634 73 -0.17679926036787141 74 -0.17513107848701914
		 75 -0.17348220782549645 76 -0.1718535352955205 77 -0.17024592792165649 78 -0.16866023337271424
		 79 -0.16709728056480905 80 -0.16555788033038377 81 -0.16404282614777554 82 -0.16255289492575375
		 83 -0.1610888478373646 84 -0.15965143119737885 85 -0.15824137737766836 86 -0.15685940575491342
		 87 -0.15550622368517919 88 -0.15418252750006822 89 -0.15288900351940637 90 -0.1516263290756642
		 91 -0.15039517354563925 92 -0.14919619938526019 93 -0.14803006316374001 94 -0.14689741659370614
		 95 -0.145798907554339 96 -0.14473518110499561 97 -0.14370688048721647 98 -0.14271464811348067
		 99 -0.14175912654151501 100 -0.14084095943341718 101 -0.13996079249930798 102 -0.13911927442566208
		 103 -0.13831705778890413 104 -0.13755479995528536 105 -0.13683316396845391 106 -0.13615281942653529
		 107 -0.13551444335091295 108 -0.13491872104925628 109 -0.13436634697568772 110 -0.13385802559129178
		 111 -0.13339447222847367 112 -0.13297641396294191 113 -0.1326045904973428 114 -0.13227975506079881
		 115 -0.13200267532879384 116 -0.13177413436802071 117 -0.1315949316109325 118 -0.13146588386483871
		 119 -0.13138782636044305 120 -0.13136161384471978;
createNode animCurveTL -n "pCube1_locator10_MKR_translateY";
	rename -uid "54D2E78D-4D2B-0AA9-885F-83AE3904F298";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 0.35836891482699085 2 0.35837968395786168
		 3 0.35841173812865657 4 0.35846468238867202 5 0.35853810257750751 6 0.35863156649800698
		 7 0.3587446250770322 8 0.35887681351658651 9 0.35902765243826751 10 0.35919664902428683
		 11 0.35938329815841596 12 0.3595870835701851 13 0.35980747898550802 14 0.36004394928665295
		 15 0.36029595168409734 16 0.36056293690237828 17 0.36084435038150664 18 0.36113963349495182
		 19 0.36144822478455318 20 0.36176956121205106 21 0.36210307942623565 22 0.36244821704397845
		 23 0.36280441394271112 24 0.36317111356117504 25 0.3635477642045688 26 0.36393382034953692
		 27 0.36432874394379111 28 0.36473200569454045 29 0.36514308633936343 30 0.3655614778926346
		 31 0.36598668486020369 32 0.3664182254146553 33 0.36685563252320397 34 0.3672984550200753
		 35 0.36774625861514765 36 0.3681986268305768 37 0.3686551618572691 38 0.36911548532320737
		 39 0.36957923896595701 40 0.37004608520204818 41 0.37051570758641827 42 0.37098781115568014
		 43 0.3714621226496444 44 0.37193839060627876 45 0.3724163853261161 46 0.37289589870301665
		 47 0.37337674391916376 48 0.37385875500316157 49 0.37434178625117587 50 0.37482571151212962
		 51 0.37531042333905806 52 0.37579583200985112 53 0.37628186442168854 54 0.37676846286456456
		 55 0.37725558368033663 56 0.37774319581475391 57 0.3782312792708491 58 0.37871982347297672
		 59 0.37920882555158442 60 0.37969828855952892 61 0.38018821963137828 62 0.38067862809767528
		 63 0.38116952356655909 64 0.38166091398546897 65 0.38215280369584548 66 0.38264519149383891
		 67 0.38313806871001788 68 0.3836314173209201 69 0.38412520810505169 70 0.38461939885557717
		 71 0.38511393266149341 72 0.38560873626852565 73 0.38610371853035019 74 0.38659876896002288
		 75 0.38709375639071175 76 0.38758852775398078 77 0.38808290698296877 78 0.38857669404687567
		 79 0.38906966412219501 80 0.38956156690514765 81 0.39005212606877426 82 0.39054103886716174
		 83 0.39102797588829374 84 0.39151258095606334 85 0.39199447118106989 86 0.39247323715892901
		 87 0.39294844331400647 88 0.393419628385697 89 0.39388630605365815 90 0.39434796569775998
		 91 0.39480407328792588 92 0.39525407239854271 93 0.39569738534166876 94 0.39613341441293426
		 95 0.39656154324372705 96 0.39698113825306658 97 0.39739155019242212 98 0.39779211577668128
		 99 0.39818215939446078 100 0.39856099489102448 101 0.39892792741718508 102 0.39928225533773065
		 103 0.39962327219312566 104 0.39995026870846884 105 0.40026253484395902 106 0.40055936188139607
		 107 0.40084004454152655 108 0.40110388312732381 109 0.40135018568855119 110 0.40157827020319969
		 111 0.40178746677157773 112 0.40197711981898321 113 0.40214659030296573 114 0.40229525792119269
		 115 0.40242252331584472 116 0.40252781027027518 117 0.40261056789336669 118 0.40267027278657064
		 119 0.40270643118803784 120 0.40271858108749325;
createNode animCurveTU -n "pCube1_locator10_MKR_enable";
	rename -uid "7E1CBB39-4F89-BFFD-3429-E4AEF2144BD4";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 122 ".ktv[0:121]"  0 0 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1
		 95 1 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1
		 110 1 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1 121 0;
createNode animCurveTU -n "pCube1_locator10_MKR_weight";
	rename -uid "08CDD9EB-4218-9662-1EB5-E891CEAF3D29";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1 10 1
		 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1 27 1
		 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1 44 1
		 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1 61 1
		 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1
		 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1 95 1
		 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1 110 1
		 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1;
createNode animCurveTL -n "pCube1_locator11_MKR_translateX";
	rename -uid "123A3CEC-4EAD-1EF7-A184-838B9783E2DA";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 -0.2941777967879341 2 -0.29415810897627886
		 3 -0.29409948009397829 4 -0.29400254888611604 5 -0.29386793746065498 6 -0.29369625228114088
		 7 -0.29348808513932789 8 -0.29324401410875461 9 -0.29296460448035649 10 -0.29265040968122252
		 11 -0.29230197217759801 12 -0.29191982436322023 13 -0.29150448943402024 14 -0.29105648225016201
		 15 -0.29057631018631702 16 -0.29006447397096941 17 -0.28952146851544841 18 -0.2889477837332638
		 19 -0.28834390535019866 20 -0.28771031570547573 21 -0.28704749454418121 22 -0.28635591980098657
		 23 -0.28563606837505778 24 -0.28488841689590505 25 -0.28411344247977355 26 -0.28331162347603434
		 27 -0.28248344020289073 28 -0.28162937567159124 29 -0.28074991629818968 30 -0.27984555260179245
		 31 -0.27891677988810615 32 -0.27796409891700047 33 -0.27698801655270799 34 -0.27598904639520394
		 35 -0.27496770939124437 36 -0.27392453442348769 37 -0.27286005887609316 38 -0.27177482917516327
		 39 -0.27066940130240552 40 -0.26954434128039512 41 -0.26840022562785232 42 -0.26723764178340947
		 43 -0.26605718849639415 44 -0.26485947618325401 45 -0.26364512724834371 46 -0.26241477636791377
		 47 -0.26116907073627471 48 -0.25990867027326364 49 -0.25863424779228816 50 -0.25734648912841163
		 51 -0.25604609322611549 52 -0.25473377218657045 53 -0.25341025127444955 54 -0.25207626888451234
		 55 -0.25073257646840436 56 -0.24937993842231504 57 -0.24801913193635272 58 -0.24665094680668509
		 59 -0.24527618521170458 60 -0.24389566145365582 61 -0.24251020166735171 62 -0.2411206434977648
		 63 -0.23972783574844636 64 -0.23833263800285576 65 -0.23693592022081861 66 -0.23553856231243153
		 67 -0.2341414536918287 68 -0.23274549281328438 69 -0.23135158669219436 70 -0.2299606504134889
		 71 -0.2285736066300571 72 -0.2271913850537477 73 -0.22581492194147434 74 -0.22444515957892075
		 75 -0.22308304576425475 76 -0.22172953329419742 77 -0.22038557945466941 78 -0.21905214551814201
		 79 -0.21773019624967416 80 -0.21642069942348419 81 -0.21512462535174959 82 -0.21384294642716623
		 83 -0.21257663668063131 84 -0.21132667135523697 85 -0.21009402649758757 86 -0.20887967856727108
		 87 -0.20768460406513867 88 -0.20650977918085328 89 -0.20535617946001472 90 -0.20422477949097007
		 91 -0.2031165526112656 92 -0.20203247063352897 93 -0.20097350359041138 94 -0.19994061949807396
		 95 -0.19893478413755861 96 -0.19795696085325604 97 -0.19700811036754712 98 -0.19608919061059266
		 99 -0.19520115656412446 100 -0.1943449601179954 101 -0.19352154993815562 102 -0.19273187134462533
		 103 -0.19197686619795917 104 -0.19125747279262173 105 -0.19057462575561135 106 -0.18992925594860538
		 107 -0.1893222903718253 108 -0.18875465206775133 109 -0.18822726002274154 110 -0.18774102906453444
		 111 -0.18729686975353355 112 -0.18689568826568426 113 -0.18653838626465535 114 -0.18622586076093617
		 115 -0.18595900395533582 116 -0.18573870306424861 117 -0.18556584012389654 118 -0.18544129177060187
		 119 -0.18536592899396581 120 -0.185340616859622;
createNode animCurveTL -n "pCube1_locator11_MKR_translateY";
	rename -uid "F874DB8E-4158-6684-735F-0DBC361C6E49";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 0.24073155249137135 2 0.24073983505834695
		 3 0.24076450268074723 4 0.24080529464935641 5 0.24086196216133371 6 0.24093426750539182
		 7 0.24102198323057999 8 0.2411248913029036 9 0.24124278225381524 10 0.24137545432442054
		 11 0.24152271260904956 12 0.24168436820169348 13 0.24186023734863349 14 0.24205014061046026
		 15 0.24225390203652486 16 0.2424713483547507 17 0.24270230817958982 18 0.24294661124079864
		 19 0.24320408763557244 20 0.24347456710646143 21 0.24375787834736506 22 0.24405384833975696
		 23 0.24436230172118389 24 0.24468306018790731 25 0.24501594193342946 26 0.24536076112447647
		 27 0.2457173274158444 28 0.24608544550533229 29 0.24646491472980991 30 0.24685552870325456
		 31 0.2472570749973928 32 0.2476693348653709 33 0.24809208300864405 34 0.24852508738704693
		 35 0.2489681090717798 36 0.24942090214078538 37 0.24988321361577137 38 0.25035478343986806
		 39 0.25083534449468514 40 0.25132462265528188 41 0.2518223368813387 42 0.25232819934259498
		 43 0.25284191557639613 44 0.25336318467500663 45 0.253891699500149 46 0.25442714692206658
		 47 0.25496920808026902 48 0.25551755866297654 49 0.25607186920219949 50 0.25663180538130304
		 51 0.2571970283518541 52 0.25776719505654433 53 0.25834195855497366 54 0.2589209683491297
		 55 0.25950387070545033 56 0.26009030897048102 57 0.26067992387722638 58 0.26127235383948055
		 59 0.2618672352315774 60 0.26246420265122472 61 0.26306288916328935 62 0.2636629265226712
		 63 0.26426394537465248 64 0.26486557543139333 65 0.2654674456235423 66 0.26606918422621839
		 67 0.26667041895894528 68 0.26727077705941249 69 0.26786988533125711 70 0.26846737016635713
		 71 0.26906285754242876 72 0.26965597299700139 73 0.27024634157912009 74 0.27083358778037725
		 75 0.27141733544711055 76 0.27199720767582125 77 0.27257282669405192 78 0.27314381372913532
		 79 0.27370978886735087 80 0.27427037090614825 81 0.27482517720216804 82 0.27537382351784545
		 83 0.27591592386940278 84 0.27645109037903071 85 0.27697893313402466 86 0.27749906005557312
		 87 0.27801107677981918 88 0.27851458655368744 89 0.2790091901478462 90 0.27949448578900915
		 91 0.279970069113612 92 0.28043553314469793 93 0.2808904682936475 94 0.28133446238816551
		 95 0.28176710072770739 96 0.28218796616729147 97 0.28259663923040512 98 0.28299269825146078
		 99 0.28337571954801266 100 0.2837452776227033 101 0.28410094539465791 102 0.28444229445980385
		 103 0.28476889537936312 104 0.28508031799552525 105 0.28537613177308807 106 0.28565590616564396
		 107 0.28591921100466566 108 0.28616561690966047 109 0.28639469571735821 110 0.28660602092772403
		 111 0.28679916816440376 112 0.28697371564704732 113 0.28712924467280154 114 0.28726534010410898
		 115 0.28738159085981074 116 0.28747759040642307 117 0.28755293724633857 118 0.28760723539958533
		 119 0.28764009487569409 120 0.28765113213212778;
createNode animCurveTU -n "pCube1_locator11_MKR_enable";
	rename -uid "64B664E4-4603-CA9F-3D6E-BE83D698467C";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 122 ".ktv[0:121]"  0 0 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1
		 95 1 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1
		 110 1 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1 121 0;
createNode animCurveTU -n "pCube1_locator11_MKR_weight";
	rename -uid "403983B4-40DD-77B9-43FD-14A76A9F803B";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1 10 1
		 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1 27 1
		 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1 44 1
		 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1 61 1
		 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1
		 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1 95 1
		 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1 110 1
		 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1;
createNode animCurveTL -n "pCube1_locator12_MKR_translateX";
	rename -uid "16035540-42AA-8B4D-6D5D-C79F3ED9006C";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 -0.26950598931324704 2 -0.26947509300197348
		 3 -0.269383089402357 4 -0.26923099091270158 5 -0.26901979027455775 6 -0.26875046208078973
		 7 -0.26842396436026211 8 -0.26804124022566816 9 -0.26760321957182065 10 -0.26711082081242421
		 11 -0.26656495264398156 12 -0.26596651582605657 13 -0.26531640496762021 14 -0.26461551030965297
		 15 -0.26386471949459539 16 -0.26306491931359244 17 -0.26221699742283083 18 -0.26132184402057224
		 19 -0.26038035347679617 20 -0.25939342590764958 21 -0.25836196868720346 22 -0.25728689788930947
		 23 -0.25616913965265559 24 -0.25500963146245853 25 -0.25380932334256923 26 -0.25256917895215042
		 27 -0.25129017658148978 28 -0.24997331004195483 29 -0.24861958944556373 30 -0.24723004187016451
		 31 -0.24580571190676193 32 -0.24434766208611086 33 -0.24285697318232236 34 -0.24133474439187558
		 35 -0.23978209338711637 36 -0.23820015624403068 37 -0.23659008724481728 38 -0.23495305855652704
		 39 -0.23329025978780671 40 -0.23160289742654594 41 -0.22989219416198792 42 -0.22815938809563346
		 43 -0.22640573184599544 44 -0.22463249155298548 45 -0.22284094578840408 46 -0.2210323843796449
		 47 -0.21920810715433747 48 -0.2173694226142 49 -0.21551764654685945 50 -0.21365410058483519
		 51 -0.21178011072123126 52 -0.2098970057919648 53 -0.20800611593457002 54 -0.20610877103372832
		 55 -0.20420629916372468 56 -0.20230002503797884 57 -0.20039126847567945 58 -0.19848134289532349
		 59 -0.19657155384469027 60 -0.19466319757639006 61 -0.19275755967769992 62 -0.19085591376287447
		 63 -0.18895952023555362 64 -0.18706962512825065 65 -0.18518745902522959 66 -0.18331423607435443
		 67 -0.18145115309273963 68 -0.17959938877024539 69 -0.17776010297407741 70 -0.17593443615692639
		 71 -0.17412350887029732 72 -0.17232842138387444 73 -0.17055025341098806 74 -0.16879006393950791
		 75 -0.16704889116675292 76 -0.16532775253634358 77 -0.16362764487427062 78 -0.16194954462088124
		 79 -0.16029440815494495 80 -0.15866317220549531 81 -0.15705675434672917 82 -0.15547605357090266
		 83 -0.15392195093387917 84 -0.15239531026777015 85 -0.15089697895495957 86 -0.14942778875771912
		 87 -0.14798855669759836 88 -0.14658008597880468 89 -0.14520316694990099 90 -0.14385857809828084
		 91 -0.14254708707209174 92 -0.14126945172452737 93 -0.14002642117568997 94 -0.13881873688756108
		 95 -0.13764713374797127 96 -0.13651234115985666 97 -0.13541508413248871 98 -0.13435608437180757
		 99 -0.1333360613674206 100 -0.13235573347428403 101 -0.13141581898754651 102 -0.13051703720948055
		 103 -0.12966010950788698 104 -0.12884576036580597 105 -0.12807471842279133 106 -0.12734771750843699
		 107 -0.12666549766923629 108 -0.12602880619024304 109 -0.12543839861335615 110 -0.12489503975438182
		 111 -0.12439950472132921 112 -0.12395257993666164 113 -0.12355506416645951 114 -0.12320776955964574
		 115 -0.12291152270056993 116 -0.12266716567835512 117 -0.1224755571764567 118 -0.12233757358587388
		 119 -0.12225411014538479 120 -0.12222608211201796;
createNode animCurveTL -n "pCube1_locator12_MKR_translateY";
	rename -uid "1DF2D2B3-4021-7858-86CE-BB8E811B3DAF";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 0.32367391150406188 2 0.32368588309862045
		 3 0.32372151858756248 4 0.32378038535613696 5 0.32386203335127184 6 0.32396599602755782
		 7 0.32409179124711684 8 0.32423892214125494 9 0.32440687794202083 10 0.32459513479183433
		 11 0.32480315653923308 12 0.32503039552857116 13 0.32527629339113773 14 0.32554028184473038
		 15 0.32582178350815338 16 0.3261202127365066 17 0.32643497648241526 18 0.32676547518761256
		 19 0.32711110370845808 20 0.32747125227813978 21 0.32784530750741314 22 0.32823265342481478
		 23 0.32863267255638062 24 0.32904474704394127 25 0.32946825980015304 26 0.32990259569749525
		 27 0.33034714278757138 28 0.33080129354616861 29 0.33126444613872219 30 0.33173600570001949
		 31 0.33221538562127573 32 0.33270200883704115 33 0.33319530910381479 34 0.33369473226172564
		 35 0.33419973747024523 36 0.33470979840854043 37 0.33522440443088697 38 0.33574306166741652
		 39 0.33626529406048467 40 0.33679064432703265 41 0.33731867483754097 42 0.33784896840249878
		 43 0.33838112895774519 44 0.338914782140602 45 0.3394495757493502 46 0.33998518007937228
		 47 0.34052128813012006 48 0.3410576156779932 49 0.34159390121123046 50 0.3421299057239775
		 51 0.34266541236782111 52 0.34320022596025801 53 0.34373417235074633 54 0.34426709764621966
		 55 0.34479886729913956 56 0.34532936506239387 57 0.34585849181650152 58 0.34638616427574509
		 59 0.34691231358093733 60 0.34743688378755744 61 0.34795983025894051 62 0.34848111797508263
		 63 0.34900071976837865 64 0.34951861449829535 65 0.35003478517752973 66 0.35054921706264275
		 67 0.35106189572249324 68 0.35157280509798128 69 0.35208192556669626 70 0.35258923202601633
		 71 0.35309469200803556 72 0.35359826383942017 73 0.35409989485889004 74 0.35459951970453096
		 75 0.35509705868253383 76 0.35559241622828019 77 0.35608547946991698 78 0.35657611690372937
		 79 0.35706417718972139 80 0.35754948807486953 81 0.35803185545052962 82 0.35851106254947407
		 83 0.35898686928700696 84 0.35945901174958661 85 0.35992720183336491 86 0.36039112703404685
		 87 0.36085045038851604 88 0.36130481056771979 89 0.36175382211942608 90 0.36219707585862093
		 91 0.36263413940253209 92 0.36306455784654623 93 0.36348785457662358 94 0.36390353221324567
		 95 0.36431107368139837 96 0.36470994340066332 97 0.36509958858911162 98 0.36547944067439153
		 99 0.36584891680516651 100 0.3662074214558817 101 0.3665543481177298 102 0.36688908106860574
		 103 0.36721099721484307 104 0.36751946799752333 105 0.36781386135621119 106 0.36809354374303593
		 107 0.36835788218011634 108 0.36860624635341388 109 0.36883801073616629 110 0.36905255673510973
		 111 0.36924927485270864 112 0.36942756685858869 113 0.36958684796328456 114 0.36972654898725466
		 115 0.36984611851787408 116 0.36994502504678306 117 0.37002275907952265 118 0.37007883520881479
		 119 0.37011279414214671 120 0.37012420467345752;
createNode animCurveTU -n "pCube1_locator12_MKR_enable";
	rename -uid "5B5EFA54-449F-B46D-427D-98B65BB49AF0";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 122 ".ktv[0:121]"  0 0 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1
		 95 1 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1
		 110 1 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1 121 0;
createNode animCurveTU -n "pCube1_locator12_MKR_weight";
	rename -uid "176AF3B5-4036-3696-BF1D-578A402726A2";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1 10 1
		 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1 27 1
		 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1 44 1
		 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1 61 1
		 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1
		 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1 95 1
		 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1 110 1
		 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1;
createNode animCurveTL -n "locator1_MKR_translateX";
	rename -uid "D1183B31-461F-9A67-B7A0-8CB71FA0A6C2";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 -0.0051838931536537514 2 -0.0051912429347101829
		 3 -0.0052131383731961467 4 -0.0052493654531274303 5 -0.0052997316104104741 6 -0.005364064521464873
		 7 -0.0054422109392994744 8 -0.0055340355735669644 9 -0.0056394200113302762 10 -0.0057582616754639493
		 11 -0.0058904728177897048 12 -0.0060359795442189723 13 -0.0061947208693331479 14 -0.0063666477979724689
		 15 -0.0065517224315594369 16 -0.0067499170970006794 17 -0.0069612134961476446 18 -0.0071856018739083205
		 19 -0.0074230802032210774 20 -0.0076736533852039823 21 -0.0079373324629018471 22 -0.0082141338471520275
		 23 -0.0085040785531790841 24 -0.0088071914466320567 25 -0.0091235004978592604 26 -0.0094530360433066618
		 27 -0.0097958300530100462 28 -0.010151915403241396 29 -0.010521325153440508 30 -0.010904091826658635
		 31 -0.011300246692813265 32 -0.011709819054138149 33 -0.012132835532291442 34 -0.012569319356667719
		 35 -0.013019289653539823 36 -0.013482760735737898 37 -0.013959741392657044 38 -0.01445023418046365
		 39 -0.014954234712460879 40 -0.015471730949651707 41 -0.016002702491626053 42 -0.016547119867987958
		 43 -0.017104943830619279 44 -0.017676124647169944 45 -0.018260601396253129 46 -0.018858301264908006
		 47 -0.019469138848991263 48 -0.020093015457242791 49 -0.0207298184198621 50 -0.021379420402526383
		 51 -0.02204167872686924 52 -0.022716434698528021 53 -0.023403512943962368 54 -0.024102720757326834
		 55 -0.024813847458775462 56 -0.025536663765656498 57 -0.026270921178141005 58 -0.027016351380907466
		 59 -0.027772665662585405 60 -0.028539554354731655 61 -0.029316686292188421 62 -0.030103708296732368
		 63 -0.030900244685992617 64 -0.031705896809665068 65 -0.032520242615107775 66 -0.033342836244442786
		 67 -0.034173207665331162 68 -0.035010862337613913 69 -0.035855280918046184 70 -0.036705919005355858
		 71 -0.037562206927876263 72 -0.038423549575998528 73 -0.03928932628167775 74 -0.040158890747217957
		 75 -0.041031571025521185 76 -0.04190666955396527 77 -0.042783463244014552 78 -0.043661203628623746
		 79 -0.044539117069422651 80 -0.045416405025601181 81 -0.046292244386325454 82 -0.047165787868426845
		 83 -0.048036164481001231 84 -0.048902480058444775 85 -0.049763817863334447 86 -0.050619239260433935
		 87 -0.051467784462970345 88 -0.052308473352178975 89 -0.053140306370975332 90 -0.053962265492446038
		 91 -0.054773315263693056 92 -0.055572403925402747 93 -0.056358464607330738 94 -0.057130416599724509
		 95 -0.057887166700521631 96 -0.058627610637983218 97 -0.059350634568227478 98 -0.060055116646952511
		 99 -0.060739928674435673 100 -0.061403937812711307 101 -0.062046008373636385 102 -0.062665003676354913
		 103 -0.063259787972477777 104 -0.06382922843710459 105 -0.064372197223605987 106 -0.064887573579892832
		 107 -0.065374246023698901 108 -0.065831114574195715 109 -0.066257093037060788 110 -0.066651111339905811
		 111 -0.067012117914767355 112 -0.067339082124143301 113 -0.067630996726839032 114 -0.067886880379668946
		 115 -0.068105780170817032 116 -0.068286774180435827 117 -0.068428974063808434 118 -0.068531527652151369
		 119 -0.068593621565876228 120 -0.068614483834854245;
createNode animCurveTL -n "locator1_MKR_translateY";
	rename -uid "5067993B-49B1-AD33-9486-36B459D08A2E";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 0.12291455750076419 2 0.1229096280105223
		 3 0.12289498415473599 4 0.12287089101501936 5 0.12283767501395759 6 0.12279572044470577
		 7 0.12274546613435833 8 0.12268740223146113 9 0.12262206710861823 10 0.12255004437167638
		 11 0.12247195996747084 12 0.12238847938258601 13 0.12230030492601551 14 0.12220817308903476
		 15 0.12211285197596278 16 0.12201513879987724 17 0.12191585743767619 18 0.12181585603921163
		 19 0.12171600468553212 20 0.12161719309155794 21 0.12152032834880744 22 0.12142633270404413
		 23 0.12133614136999826 24 0.12125070036454377 25 0.12117096437496977 26 0.12109789464422027
		 27 0.12103245687620423 28 0.12097561915750865 29 0.12092834989307066 30 0.1208916157535902
		 31 0.12086637963267777 32 0.12085359861196465 33 0.12085422193260831 34 0.1208691889718575
		 35 0.12089942722356295 36 0.12094585028173044 37 0.12100935582646166 38 0.12109082361183154
		 39 0.12119111345550182 40 0.12131106323009178 41 0.12145148685656859 42 0.12161317230016544
		 43 0.1217968795695642 44 0.12200333872034341 45 0.12223324786392775 46 0.12248727118353364
		 47 0.12276603695886112 48 0.12307013560152935 49 0.12340011770352222 50 0.12375649210115991
		 51 0.12413972395737427 52 0.12455023286532296 53 0.1249883909766345 54 0.12545452115782973
		 55 0.12594889517871244 56 0.12647173193678096 57 0.12702319572193688 58 0.12760339452601566
		 59 0.12821237840188482 60 0.12885013787707855 61 0.12951660242713636 62 0.13021163901402721
		 63 0.13093505069520472 64 0.13168657530902816 65 0.13246588424242489 66 0.13327258128681507
		 67 0.13410620158843678 68 0.13496621069931358 69 0.13585200373518214 70 0.13676290464675878
		 71 0.13769816561076142 72 0.13865696654710802 73 0.13963841476871131 74 0.14064154477023894
		 75 0.14166531816214978 76 0.14270862375622995 77 0.14377027780871909 78 0.14484902442698777
		 79 0.14594353614554145 80 0.14705241467692676 81 0.14817419184289049 82 0.14930733069087743
		 83 0.15045022680067976 84 0.15160120978572689 85 0.15275854499318764 86 0.15392043540667621
		 87 0.15508502375499045 88 0.15625039482988956 89 0.15741457801550196 90 0.15857555003150359
		 91 0.15973123789174448 92 0.16087952207952194 93 0.16201823994019438 94 0.1631451892913347
		 95 0.16425813225008701 96 0.16535479927686181 97 0.16643289343396672 98 0.16749009485721311
		 99 0.1685240654379847 100 0.16953245371268988 101 0.17051289995595276 102 0.17146304147331903
		 103 0.17238051808868238 104 0.17326297782104827 105 0.17410808274467104 106 0.17491351502600716
		 107 0.17567698313033486 108 0.17639622819028566 109 0.1770690305279301 110 0.17769321632144319
		 111 0.17826666440674932 112 0.17878731320391306 113 0.17925316775739741 114 0.17966230687864693
		 115 0.18001289037877866 116 0.18030316637847066 117 0.18053147868143149 118 0.18069627419709144
		 119 0.18079611039742305 120 0.18082966279200929;
createNode animCurveTU -n "locator1_MKR_enable";
	rename -uid "F33FEFB3-4F15-47F6-CA2F-5C9CED62D956";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 122 ".ktv[0:121]"  0 0 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1
		 95 1 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1
		 110 1 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1 121 0;
createNode animCurveTU -n "locator1_MKR_weight";
	rename -uid "1B18AA66-4027-3ADD-25D2-28A22A2A8AE6";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1 10 1
		 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1 27 1
		 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1 44 1
		 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1 61 1
		 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1
		 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1 95 1
		 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1 110 1
		 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1;
createNode animCurveTL -n "locator2_MKR_translateX";
	rename -uid "030B48C6-4308-2A5D-1D5A-B8A3384BB192";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 -0.078111954852550847 2 -0.078130489042386175
		 3 -0.078185697664791332 4 -0.078277023885635899 5 -0.078403954308986445 6 -0.078566016559358853
		 7 -0.078762776970817794 8 -0.078993838374539826 9 -0.079258837976982799 10 -0.079557445321283837
		 11 -0.079889360324956193 12 -0.080254311387372601 13 -0.08065205356091143 14 -0.08108236677999392
		 15 -0.081545054142588336 16 -0.08203994023905764 17 -0.082566869523530373 18 -0.08312570472324321
		 19 -0.083716325281566528 20 -0.084338625830662928 21 -0.084992514689965715 22 -0.085677912386880828
		 23 -0.086394750196320425 24 -0.087142968695885559 25 -0.087922516333699741 26 -0.088733348006085344
		 27 -0.089575423642451746 28 -0.090448706794949707 29 -0.091353163230604051 30 -0.092288759523822539
		 31 -0.093255461647339666 32 -0.094253233559824123 33 -0.095282035788547881 34 -0.096341824005683918
		 35 -0.097432547596971841 36 -0.098554148221660198 37 -0.099706558362815889 38 -0.10088969986726232
		 39 -0.10210348247460055 40 -0.1033478023349455 41 -0.10462254051520481 42 -0.10592756149392868
		 43 -0.10726271164494972 44 -0.10862781771025026 45 -0.11002268526269932 46 -0.11144709715951984
		 47 -0.11290081198757335 48 -0.11438356250177495 49 -0.11589505405818223 50 -0.11743496304354517
		 51 -0.11900293530334349 52 -0.1205985845705837 53 -0.12222149089788181 54 -0.12387119909560573
		 55 -0.12554721717910972 56 -0.12724901482834894 57 -0.12897602186341856 58 -0.13072762673981553
		 59 -0.13250317506747999 60 -0.13430196815792017 61 -0.13612326160397403 62 -0.13796626389700095
		 63 -0.13983013508653264 64 -0.14171398548763603 65 -0.14361687444145865 66 -0.1455378091346296
		 67 -0.14747574348338199 68 -0.14942957708843124 69 -0.15139815426681436 70 -0.15338026316702125
		 71 -0.15537463497388004 72 -0.15737994320975091 73 -0.15939480313865578 74 -0.16141777128002754
		 75 -0.16344734503877134 76 -0.16548196245834368 77 -0.16752000210349982 78 -0.16955978307930947
		 79 -0.17159956519293529 80 -0.17363754926454111 81 -0.17567187759353375 82 -0.17770063458614527
		 83 -0.1797218475501316 84 -0.18173348766209585 85 -0.18373347111264771 86 -0.18571966043427718
		 87 -0.18768986601645321 88 -0.18964184781205068 89 -0.19157331723879401 90 -0.19348193927892576
		 91 -0.19536533477982465 92 -0.19722108295777929 93 -0.1990467241065681 94 -0.20083976251193214
		 95 -0.2025976695724252 96 -0.20431788712651522 97 -0.20599783098516289 98 -0.20763489466846474
		 99 -0.20922645334425927 100 -0.21076986796592129 101 -0.2122624896058698 102 -0.21370166398060153
		 103 -0.2150847361623428 104 -0.21640905547169575 105 -0.21767198054490555 106 -0.21887088456864257
		 107 -0.22000316067444603 108 -0.22106622748421784 109 -0.22205753479740675 110 -0.22297456940974869
		 111 -0.2238148610526709 112 -0.22457598844169191 113 -0.22525558542136614 114 -0.22585134719354971
		 115 -0.22636103661495977 116 -0.22678249054921923 117 -0.2271136262577691 118 -0.22735244781322705
		 119 -0.22749705251796698 120 -0.22754563730987482;
createNode animCurveTL -n "locator2_MKR_translateY";
	rename -uid "CBA99A5B-49B8-FE51-91BC-8A880AEE0AD6";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 -0.022839268259642664 2 -0.022843415520741095
		 3 -0.022855719536383046 4 -0.022875909986129539 5 -0.022903635388975496 6 -0.02293846757689294
		 7 -0.022979905955253788 8 -0.023027381567403804 9 -0.023080260979535583 10 -0.023137850000975679
		 11 -0.023199397254064114 12 -0.023264097606923162 13 -0.023331095481621211 14 -0.023399488049476891
		 15 -0.023468328324588394 16 -0.023536628166014206 17 -0.023603361198462069 18 -0.023667465660786591
		 19 -0.023727847191091223 20 -0.023783381556754135 21 -0.023832917337249793 22 -0.023875278567227654
		 23 -0.023909267346896412 24 -0.023933666426405098 25 -0.023947241770542693 26 -0.023948745109732383
		 27 -0.023936916482969139 28 -0.023910486778025042 29 -0.02386818027392601 30 -0.02380871719039801
		 31 -0.023730816248668241 32 -0.023633197247700077 33 -0.023514583659632937 34 -0.023373705247885845
		 35 -0.023209300711061975 36 -0.023020120355483509 37 -0.022804928798835 38 -0.022562507707074186
		 39 -0.022291658566407246 40 -0.021991205491769916 41 -0.021659998072882103 42 -0.02129691425855218
		 43 -0.020900863279515736 44 -0.02047078860966306 45 -0.020005670965092037 46 -0.019504531339964715
		 47 -0.01896643407768317 48 -0.018390489975427915 49 -0.017775859419589257 50 -0.017121755549123152
		 51 -0.016427447443327137 52 -0.015692263329986134 53 -0.014915593809285699 54 -0.014096895088310524
		 55 -0.013235692220377349 56 -0.01233158234283227 57 -0.011384237906371719 58 -0.010393409888312444
		 59 -0.0093589309816360378 60 -0.0082807187510121616 61 -0.0071587787464001962 62 -0.0059932075642034066
		 63 -0.0047841958453653799 64 -0.0035320311991896558 65 -0.0022371010410965342 66 -0.00089989533196588312
		 67 0.00047899079382229814 68 0.0018988545250523403 69 0.003358883008919844 70 0.0048581511391958543
		 71 0.0063956195120399295 72 0.0079701325645619159 73 0.0095804169115509819 74 0.011225079896044154
		 75 0.012902608369614543 76 0.014611367718407431 77 0.016349601151015358 78 0.018115429264304539
		 79 0.019906849903224 80 0.021721738330489959 81 0.023557847721808245 82 0.025412810001987141
		 83 0.027284137036894807 84 0.029169222195727373 85 0.031065342297484588 86 0.032969659954865005
		 87 0.034879226328052404 88 0.036790984299991281 89 0.038701772083816754 90 0.040608327272054545
		 91 0.042507291336088326 92 0.044395214583162312 93 0.046268561576886524 94 0.048123717025826185
		 95 0.049956992143279533 96 0.05176463147980237 97 0.05354282022841883 98 0.055287692000763222
		 99 0.056995337070637753 100 0.058661811079661064 101 0.060283144197803673 102 0.061855350729677516
		 103 0.063374439155490681 104 0.064836422593547938 105 0.066237329669143863 106 0.067573215772611439
		 107 0.068840174687184397 108 0.070034350565204462 109 0.071151950229065841 110 0.072189255771134997
		 111 0.073142637424720269 112 0.074008566676011966 113 0.074783629584750599 114 0.075464540279240877
		 115 0.076048154589188566 116 0.076531483777734888 117 0.076911708331982021 118 0.077186191769248458
		 119 0.077352494414311135 120 0.077408387100926457;
createNode animCurveTU -n "locator2_MKR_enable";
	rename -uid "AA146F45-4B30-9B8D-F227-85861565B7E2";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 122 ".ktv[0:121]"  0 0 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1
		 95 1 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1
		 110 1 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1 121 0;
createNode animCurveTU -n "locator2_MKR_weight";
	rename -uid "AD6CAF10-437C-A82C-DC85-D8961F99CAD8";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1 10 1
		 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1 27 1
		 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1 44 1
		 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1 61 1
		 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1
		 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1 95 1
		 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1 110 1
		 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1;
createNode animCurveTL -n "locator3_MKR_translateX";
	rename -uid "13DEE731-48E0-72E5-F551-FEABB300B6AA";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 0.072124521331047631 2 0.072115550766623571
		 3 0.0720888214353399 4 0.072044578430822237 5 0.071983030556121097 6 0.071904352277577743
		 7 0.071808685569067832 8 0.071696141656023782 9 0.071566802667973994 10 0.071420723207737513
		 11 0.071257931844874389 12 0.071078432540489067 13 0.070882206010033477 14 0.07066921103035595
		 15 0.070439385696849821 16 0.070192648636233868 17 0.069928900180169729 18 0.069648023504647161
		 19 0.069349885739803829 20 0.069034339054610538 21 0.068701221720634087 22 0.068350359158886875
		 23 0.067981564973594422 24 0.067594641976533754 25 0.06718938320543888 26 0.066765572939824214
		 27 0.066322987717435944 28 0.065861397354401108 29 0.065380565972036675 30 0.064880253033138491
		 31 0.064360214390468129 32 0.063820203350031246 33 0.063259971751632227 34 0.062679271069069342
		 35 0.062077853532224281 36 0.061455473273177685 37 0.060811887498360084 38 0.06014685768862571
		 39 0.059460150828993918 40 0.05875154066967625 41 0.058020809019849962 42 0.057267747075484432
		 43 0.056492156782366187 44 0.055693852235284225 45 0.054872661114151122 46 0.054028426157637255
		 47 0.053161006674672939 48 0.052270280093949295 49 0.05135614355130258 50 0.050418515514605078
		 51 0.049457337445506511 52 0.048472575497080506 53 0.047464222246110244 54 0.046432298458427668
		 55 0.045376854885362694 56 0.044297974088998049 57 0.043195772293536772 58 0.042070401259691415
		 59 0.040922050178576641 60 0.039750947581154494 61 0.038557363258824418 62 0.037341610190281926
		 63 0.036104046469284001 64 0.034845077227466326 65 0.033565156545846242 66 0.032264789348129375
		 67 0.030944533268417174 68 0.029605000485385058 69 0.02824685951446726 70 0.026870836949067334
		 71 0.025477719141282718 72 0.024068353812128351 73 0.022643651580743995 74 0.02120458740158615
		 75 0.019752201898159183 76 0.018287602581397167 77 0.016811964940427249 78 0.015326533393077546
		 79 0.013832622083185253 80 0.012331615511500083 81 0.010824968986769323 82 0.0093142088834519132
		 83 0.0078009326924349809 84 0.0062868088511285336 85 0.004773576339401342 86 0.003263044027982831
		 87 0.0017570897662343432 88 0.00025765919655129643 89 -0.0012332357168778896 90 -0.0027135184566434711
		 91 -0.004181050029014699 92 -0.0056336313593609577 93 -0.0070690060153496548 94 -0.0084848632661259638
		 95 -0.009878841484498746 96 -0.011248531897857739 97 -0.01259148269210647 98 -0.01390520347135632
		 99 -0.015187170074435374 100 -0.016434829747482171 101 -0.017645606669984493 102 -0.018816907829602325
		 103 -0.019946129239002408 104 -0.021030662485724827 105 -0.022067901603805451 106 -0.023055250253521231
		 107 -0.023990129193206589 108 -0.02486998402461682 109 -0.025692293190834548 110 -0.026454576203190916
		 111 -0.02715440207118619 112 -0.02778939790690621 113 -0.028357257672995795 114 -0.028855751040882505
		 115 -0.029282732323646699 116 -0.029636149445763205 117 -0.029914052909881139 118 -0.030114604718914917
		 119 -0.030236087209997209 120 -0.030276911755320768;
createNode animCurveTL -n "locator3_MKR_translateY";
	rename -uid "68C68FBC-449C-1131-C383-AA89B1F96DF7";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 -0.13833241711119637 2 -0.13834625927894595
		 3 -0.13838743114036783 4 -0.13845533934243315 5 -0.13854931221321631 6 -0.13866860396350933
		 7 -0.13881239864713368 8 -0.13897981390070113 9 -0.13916990448208821 10 -0.13938166562554333
		 11 -0.13961403623013102 12 -0.13986590189710668 13 -0.1401360978308297 14 -0.14042341161688843
		 15 -0.14072658589031917 16 -0.14104432090602709 17 -0.14137527702285768 18 -0.14171807711214623
		 19 -0.14207130890101183 20 -0.14243352726016006 21 -0.1428032564454913 22 -0.14317899230239411
		 23 -0.14355920444120907 24 -0.14394233839200354 25 -0.14432681774646561 26 -0.14471104629442066
		 27 -0.14509341016219462 28 -0.14547227995978246 29 -0.14584601294352773 30 -0.14621295520077587
		 31 -0.14657144386273169 32 -0.14691980935152466 33 -0.14725637766725519 34 -0.14757947272056904
		 35 -0.14788741871607192 36 -0.1481785425916689 37 -0.14845117651864953 38 -0.1487036604670976
		 39 -0.14893434484092438 40 -0.14914159318653247 41 -0.14932378497882065 42 -0.14947931848789336
		 43 -0.14960661372950557 44 -0.14970411550187401 45 -0.14977029651109208 46 -0.1498036605869365
		 47 -0.14980274599038801 48 -0.14976612881367479 49 -0.14969242647310677 50 -0.14958030129438138
		 51 -0.14942846418941969 52 -0.14923567842312163 53 -0.14900076346772317 54 -0.14872259894167622
		 55 -0.14840012862918373 56 -0.14803236457566182 57 -0.1476183912535205 58 -0.14715736979171734
		 59 -0.14664854226154411 60 -0.14609123601009338 61 -0.14548486803178434 62 -0.14482894936720003
		 63 -0.14412308951736869 64 -0.14336700086042042 65 -0.14256050305634915 66 -0.14170352742437226
		 67 -0.14079612127612584 68 -0.13983845218665292 69 -0.13883081218387755 70 -0.13777362183596531
		 71 -0.13666743421470856 72 -0.13551293871181974 73 -0.134310964683786 74 -0.13306248489975586
		 75 -0.13176861876579021 76 -0.13043063529772475 77 -0.12904995581390394 78 -0.12762815631811697
		 79 -0.12616696954226481 80 -0.12466828661759077 81 -0.12313415834274088 82 -0.12156679601650705
		 83 -0.11996857180285653 84 -0.11834201859577104 85 -0.11668982935153865 86 -0.11501485585648197
		 87 -0.11332010689863853 88 -0.1116087458127204 89 -0.10988408736871086 90 -0.10814959397576984
		 91 -0.10640887117469822 92 -0.10466566239408404 93 -0.10292384294742096 94 -0.10118741325094416
		 95 -0.099460491244709237 96 -0.097747304002516411 97 -0.096052178519665299 98 -0.094379531671226091
		 99 -0.092733859337503888 100 -0.091119724697657722 101 -0.08954174569700929 102 -0.088004581698410966
		 103 -0.086512919333122051 104 -0.085071457571966436 105 -0.083684892043054904 106 -0.082357898628051429
		 107 -0.081095116374805765 108 -0.079901129770121593 109 -0.078780450422454129 110 -0.077737498210383671
		 111 -0.076776581958757584 112 -0.075901879710373654 113 -0.075117418666950209 114 -0.074427054878841992
		 115 -0.073834452768461123 116 -0.07334306457758305 117 -0.072956109833618776 118 -0.072676554934450133
		 119 -0.072507092955479135 120 -0.072450123786122922;
createNode animCurveTU -n "locator3_MKR_enable";
	rename -uid "C65AD64B-4620-C007-E315-04B052820FFD";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 122 ".ktv[0:121]"  0 0 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1
		 95 1 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1
		 110 1 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1 121 0;
createNode animCurveTU -n "locator3_MKR_weight";
	rename -uid "8E3B21C9-4FB9-F1CC-9F4B-499FD63F057A";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1 10 1
		 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1 27 1
		 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1 44 1
		 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1 61 1
		 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1
		 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1 95 1
		 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1 110 1
		 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1;
createNode animCurveTL -n "locator4_MKR_translateX";
	rename -uid "9288ED9C-446C-D2BB-48C6-85A3EF986493";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 0.083289732255346527 2 0.08328354031069074
		 3 0.083265088471542903 4 0.083234540391999845 5 0.083192031238020103 6 0.083137669233718237
		 7 0.083071537125485984 8 0.082993693570893146 9 0.08290417445884013 10 0.082802994167009203
		 11 0.082690146762268824 12 0.082565607149324149 13 0.082429332172572756 14 0.082281261675838602
		 15 0.08212131952435997 16 0.081949414593173064 17 0.081765441725789145 18 0.081569282666851151
		 19 0.081360806972261002 20 0.081139872900085952 21 0.080906328285380913 22 0.080660011401909038
		 23 0.08040075181359907 24 0.080128371218436412 25 0.079842684287357746 26 0.079543499500600579
		 27 0.07923061998383929 28 0.078903844346325136 29 0.078562967523151284 30 0.078207781623644945
		 31 0.077838076787796084 32 0.077453642052527027 33 0.077054266229504398 34 0.076639738796094981
		 35 0.076209850800961765 36 0.075764395785691718 37 0.075303170723735491 38 0.07482597697783222
		 39 0.074332621276968602 40 0.073822916713806364 41 0.073296683763380943 42 0.072753751323740845
		 43 0.072193957779059681 44 0.07161715208560171 45 0.071023194880766694 46 0.070411959615282127
		 47 0.069783333708425155 48 0.069137219725989962 49 0.068473536580515137 50 0.067792220753089993
		 51 0.067093227535843791 52 0.066376532294008195 53 0.065642131746203924 54 0.064890045261373541
		 55 0.064120316170519942 56 0.063333013091161128 57 0.062528231262135803 58 0.061706093886121693
		 59 0.060866753476940483 60 0.060010393208430601 61 0.059137228261369579 62 0.058247507164624013
		 63 0.05734151312639324 64 0.05641956535110304 65 0.05548202033718741 66 0.054529273150686008
		 67 0.053561758669266712 68 0.052579952790980267 69 0.051584373601740396 70 0.050575582495234417
		 71 0.049554185238676829 72 0.048520832977547945 73 0.047476223172197796 74 0.046421100458952758
		 75 0.045356257428147639 76 0.044282535311297666 77 0.04320082456946206 78 0.042112065374705132
		 79 0.041017247976451121 80 0.039917412944455388 81 0.038813651280077965 82 0.03770710438755287
		 83 0.036598963896994463 84 0.035490471330983375 85 0.034382917606721186 86 0.033277642365938664
		 87 0.032176033125006054 88 0.031079524238005751 89 0.029989595665890101 90 0.028907771545294225
		 91 0.027835618551061869 92 0.026774744047097343 93 0.025726794020789923 94 0.024693450796933192
		 95 0.023676430527822312 96 0.02267748045701734 97 0.021698375955149563 98 0.020740917327074282
		 99 0.019806926390682378 100 0.018898242828731204 101 0.018016720316166301 102 0.017164222426565456
		 103 0.0163426183225448 104 0.015553778236210958 105 0.014799568747037029 106 0.014081847865854091
		 107 0.013402459934997779 108 0.012763230356019339 109 0.012165960157742406 110 0.011612420418845248
		 111 0.011104346560523504 112 0.010643432526171726 113 0.010231324866381564 114 0.0098696167488815378
		 115 0.0095598419143523294 116 0.0093034686002935185 117 0.0091018934563242837 118 0.0089564354754297915
		 119 0.0088683299667223769 120 0.0088387225962636151;
createNode animCurveTL -n "locator4_MKR_translateY";
	rename -uid "3F1120B6-4CEB-671C-77BE-4EA8C8F6D9D2";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 -0.069138083097553982 2 -0.069148956334597278
		 3 -0.069181289813441071 4 -0.069234594969887708 5 -0.069308307727283802 6 -0.06940179260660112
		 7 -0.069514346622094825 8 -0.069645202980441412 9 -0.069793534600030682 10 -0.069958457465967627
		 11 -0.070139033835326214 12 -0.070334275306258631 13 -0.070543145763729942 14 -0.070764564213848802
		 15 -0.070997407518083755 16 -0.071240513037979625 17 -0.071492681200412689 18 -0.071752677992868996
		 19 -0.072019237397728975 20 -0.072291063774085451 21 -0.072566834195187113 22 -0.072845200749216299
		 23 -0.073124792810727368 24 -0.073404219289745609 25 -0.073682070865193461 26 -0.073956922209009401
		 27 -0.074227334207037143 28 -0.074491856182486382 29 -0.074749028127498118 30 -0.074997382948086444
		 31 -0.075235448727474674 32 -0.075461751012591449 33 -0.075674815128237038 34 -0.075873168523177048
		 35 -0.076055343152157229 36 -0.076219877897578003 37 -0.07636532103427679 38 -0.076490232740599406
		 39 -0.076593187658635986 40 -0.076672777506187451 41 -0.076727613742713363 42 -0.076756330291153696
		 43 -0.076757586317176107 44 -0.076730069067002971 45 -0.076672496764582654 46 -0.076583621568438287
		 47 -0.076462232588083212 48 -0.076307158959419086 49 -0.07611727297803228 50 -0.07589149328878303
		 51 -0.075628788129528723 52 -0.075328178626243802 53 -0.074988742136196662 54 -0.07460961563520474
		 55 -0.074189999144342322 56 -0.073729159190770055 57 -0.073226432296665589 58 -0.072681228489488603
		 59 -0.072093034826053726 60 -0.071461418922114106 61 -0.070786032478363348 62 -0.070066614792936133
		 63 -0.069302996249683946 64 -0.068495101770649991 65 -0.067642954220334228 66 -0.066746677748497518
		 67 -0.065806501057411926 68 -0.064822760578630179 69 -0.063795903543537091 70 -0.062726490931135193
		 71 -0.061615200275752513 72 -0.060462828316612982 73 -0.059270293470504887 74 -0.058038638108129703
		 75 -0.056769030614108373 76 -0.055462767210072261 77 -0.054121273519804558 78 -0.052746105854989456
		 79 -0.051338952199822263 80 -0.049901632872516366 81 -0.048436100841624308 82 -0.046944441675089432
		 83 -0.04542887310005761 84 -0.043891744151717982 85 -0.04233553388981165 86 -0.040762849661972855
		 87 -0.039176424893711315 88 -0.037579116385676015 89 -0.035973901099801753 90 -0.034363872417084163
		 91 -0.032752235851025935 92 -0.031142304202273652 93 -0.029537492141615052 94 -0.027941310210311876
		 95 -0.026357358228746908 96 -0.024789318106521296 97 -0.023240946049466416 98 -0.021716064161536874
		 99 -0.020218551442205024 100 -0.018752334182784602 101 -0.017321375768073244 102 -0.015929665892795486
		 103 -0.014581209205542345 104 -0.013280013396249679 105 -0.012030076746686491 106 -0.010835375166952432
		 107 -0.0096998487445819626 108 -0.0086273878365041301 109 -0.0076218187377962709
		 110 -0.0066868889648750152 111 -0.0058262521944745793 112 -0.0050434529034381059
		 113 -0.0043419107579791283 114 -0.0037249048046246735 115 -0.0031955575185216856
		 116 -0.0027568187681146217 117 -0.0024114497583966887 118 -0.0021620070179495521
		 119 -0.0020108264977763413 120 -0.0019600078525170428;
createNode animCurveTU -n "locator4_MKR_enable";
	rename -uid "1E026C1E-4443-31D8-3D70-6C8E5ED7A796";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 122 ".ktv[0:121]"  0 0 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1
		 95 1 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1
		 110 1 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1 121 0;
createNode animCurveTU -n "locator4_MKR_weight";
	rename -uid "223089BC-4905-4452-C4BC-F09E9C1A0A32";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1 10 1
		 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1 27 1
		 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1 44 1
		 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1 61 1
		 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1
		 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1 95 1
		 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1 110 1
		 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1;
createNode animCurveTL -n "locator5_MKR_translateX";
	rename -uid "805AA252-4686-12E4-1AAB-ABAAA5C18974";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 0.11811604564571732 2 0.11811463741239725
		 3 0.1181104343684799 4 0.11810345451285598 5 0.1180936973735166 6 0.11808114501424449
		 7 0.11806576298931604 8 0.11804750125058838 9 0.11802629501105089 10 0.118002065568661
		 11 0.11797472109404095 12 0.11794415738538466 13 0.11791025859372084 14 0.1178728979214988
		 15 0.11783193829727079 16 0.11778723302910743 17 0.11773862643921684 18 0.11768595448211328
		 19 0.11762904534854557 20 0.11756772005728955 21 0.11750179303678543 22 0.11743107269850672
		 23 0.1173553620038511 24 0.11727445902624867 25 0.11718815751009526 26 0.11709624742804425
		 27 0.11699851553810126 28 0.1168947459418912 29 0.11678472064540135 30 0.11666822012341571
		 31 0.11654502388879617 32 0.1164149110676872 33 0.11627766098164971 34 0.11613305373765714
		 35 0.11598087082681374 36 0.11582089573257526 37 0.11565291454918114 38 0.11547671661092096
		 39 0.11529209513277916 40 0.11509884786291602 41 0.11489677774735285 42 0.11468569360713643
		 43 0.11446541082816231 44 0.11423575206373748 45 0.11399654794985115 46 0.11374763783302477
		 47 0.11348887051048318 48 0.11322010498228197 49 0.11294121121489764 50 0.11265207091565765
		 51 0.11235257831725398 52 0.11204264097144834 53 0.11172218055092931 54 0.11139113365813991
		 55 0.11104945263973831 56 0.11069710640519881 57 0.11033408124790356 58 0.10996038166691324
		 59 0.10957603118743453 60 0.10918107317784376 61 0.10877557166094876 62 0.10835961211700829
		 63 0.10793330227585418 64 0.10749677289529758 65 0.1070501785228265 66 0.10659369823744558
		 67 0.1061275363683406 68 0.10565192318690331 69 0.10516711556848979 70 0.10467339762015682
		 71 0.10417108127047237 72 0.10366050681738237 73 0.10314204342999611 74 0.10261608960004998
		 75 0.10208307353872836 76 0.10154345351443705 77 0.10099771812707881 78 0.10044638651433369
		 79 0.099890008485433279 80 0.099329164577916296 81 0.098764466032875142 82 0.098196554684253812
		 83 0.097626102757820465 84 0.097053812575541465 85 0.096480416161201177 86 0.095906674743259313
		 87 0.095333378151117865 88 0.094761344101178868 89 0.094191417369296815 90 0.093624468846507103
		 91 0.093061394475201231 92 0.092503114063237857 93 0.091950569973842544 94 0.091404725689525401
		 95 0.090866564248660575 96 0.090337086553811119 97 0.08981730955135625 98 0.089308264282465077
		 99 0.088810993805992555 100 0.088326550994412667 101 0.087855996204474041 102 0.087400394824856731
		 103 0.086960814703719747 104 0.086538323459650734 105 0.086133985680185043 106 0.085748860012711647
		 107 0.085383996153254094 108 0.085040431739300426 109 0.084719189153529273 110 0.084421272245983947
		 111 0.084147662982920424 112 0.083899318031255721 113 0.083677165288219779 114 0.083482100366483736
		 115 0.083314983045712832 116 0.083176633702119251 117 0.083067829728234011 118 0.082989301955708195
		 119 0.082941731094531512 120 0.082925744202603568;
createNode animCurveTL -n "locator5_MKR_translateY";
	rename -uid "3432D3AD-4BF1-394F-AE14-DF92E04D1EB8";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 0.036844843002322603 2 0.036837235609998853
		 3 0.036814623472568142 4 0.036777377119686316 5 0.036725937780695994 6 0.036660813469664988
		 7 0.036582575250630134 8 0.036491853668753627 9 0.036389335334027773 10 0.036275759645016392
		 11 0.036151915640904919 12 0.036018638970857997 13 0.035876808970338625 14 0.035727345834678736
		 15 0.035571207880731204 16 0.035409388887985838 17 0.035242915510999895 18 0.035072844755455246
		 19 0.034900261510576569 20 0.034726276131031741 21 0.034552022061814736 22 0.034378653499945844
		 23 0.034207343087167774 24 0.03403927962811093 25 0.03387566582870738 26 0.033717716049919466
		 27 0.033566654072115676 28 0.033423710865699396 29 0.033290122363854091 30 0.033167127233525995
		 31 0.033055964641017122 32 0.032957872008817612 33 0.032874082760552814 34 0.032805824051183707
		 35 0.032754314479854774 36 0.032720761783038177 37 0.032706360505911247 38 0.032712289650157156
		 39 0.032739710296682101 40 0.032789763202024536 41 0.032863566367535069 42 0.03296221258073051
		 43 0.033086766928532074 44 0.03323826428245491 45 0.033417706756150634 46 0.033626061136077356
		 47 0.033864256286441852 48 0.034133180529950735 49 0.034433679006311224 50 0.034766551010836366
		 51 0.035132547315938845 52 0.035532367478743998 53 0.035966657138498781 54 0.03643600530793023
		 55 0.036940941663166194 56 0.037481933837339332 57 0.038059384723465706 58 0.038673629792702502
		 59 0.039324934434594616 60 0.040013491326422068 61 0.0407394178392676 62 0.041502753488946387
		 63 0.042303457440421965 64 0.043141406074849953 65 0.044016390628868862 66 0.044928114916237605
		 67 0.045876193142380117 68 0.046860147822842646 69 0.047879407817087438 70 0.04893330648944394
		 71 0.050021080009404084 72 0.051141865803782105 73 0.052294701173556835 74 0.05347852208846815
		 75 0.054692162172650605 76 0.055934351894755041 77 0.05720371797611068 78 0.058498783030545565
		 79 0.059817965449470156 80 0.061159579545763343 81 0.062521835969870487 82 0.063902842411312388
		 83 0.065300604598534151 84 0.066713027609666575 85 0.068137917506355339 86 0.069572983302287672
		 87 0.071015839277483117 88 0.072464007648720852 89 0.073914921605742978 90 0.07536592872202319
		 91 0.076814294747982625 92 0.078257207793526407 93 0.079691782905686792 94 0.081115067046007794
		 95 0.082524044471047331 96 0.083915642518061162 97 0.085286737796537393 98 0.086634162784780089
		 99 0.087954712829209081 100 0.089245153542444999 101 0.090502228594585898 102 0.091722667890367982
		 103 0.092903196123140463 104 0.094040541694762281 105 0.095131445988681951 106 0.096172672981569729
		 107 0.097161019176947527 108 0.098093323842322611 109 0.098966479529364326 110 0.099777442854695919
		 111 0.10052324551688552 112 0.10120100552325573 113 0.10180793859815562 114 0.10234136974239982
		 115 0.10279874491164553 116 0.10317764277959951 117 0.10347578655009992 118 0.10369105578031623
		 119 0.10382149817560105 120 0.1038653413148497;
createNode animCurveTU -n "locator5_MKR_enable";
	rename -uid "645C36FD-459D-CDFE-4010-CE9BD4A35754";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 122 ".ktv[0:121]"  0 0 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1
		 95 1 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1
		 110 1 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1 121 0;
createNode animCurveTU -n "locator5_MKR_weight";
	rename -uid "CAF6FED0-4E28-AA93-C690-88A9E17ECB66";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1 10 1
		 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1 27 1
		 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1 44 1
		 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1 61 1
		 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1
		 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1 95 1
		 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1 110 1
		 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1;
createNode animCurveTL -n "locator6_MKR_translateX";
	rename -uid "7FE9AB35-4170-9268-6206-A3A5732E47A5";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 0.13261428047696922 2 0.13261446218215633
		 3 0.13261499457104131 4 0.1326158461479976 5 0.13261696959856806 6 0.13261830265216401
		 7 0.13261976890041749 8 0.13262127857492301 9 0.1326227292878539 10 0.13262400673871733
		 11 0.1326249853903092 12 0.13262552911673497 13 0.13262549182618788 14 0.13262471806102827
		 15 0.13262304357753885 16 0.13262029590761393 17 0.13261629490450422 18 0.13261085327461986
		 19 0.13260377709729387 20 0.13259486633430129 21 0.13258391533083347 22 0.13257071330954151
		 23 0.13255504485917768 24 0.13253669041928384 25 0.13251542676229866 26 0.13249102747438724
		 27 0.13246326343622383 28 0.13243190330488719 29 0.13239671399797182 30 0.13235746118094227
		 31 0.13231390975869917 32 0.13226582437226031 33 0.13221296990139453 34 0.13215511197398078
		 35 0.13209201748280186 36 0.13202345511040714 37 0.131949195862618 38 0.13186901361117276
		 39 0.13178268564593498 40 0.13168999323701469 41 0.13159072220707257 42 0.13148466351399146
		 43 0.13137161384402063 44 0.13125137621540461 45 0.13112376059241615 46 0.13098858450962303
		 47 0.13084567370611 48 0.130694862769279 49 0.13053599578774555 50 0.13036892701273362
		 51 0.13019352152725872 52 0.13000965592227287 53 0.1298172189788187 54 0.12961611235512271
		 55 0.12940625127742211 56 0.12918756523319552 57 0.12895999866533014 58 0.12872351166563012
		 59 0.12847808066592736 60 0.12822369912492504 61 0.12796037820876283 62 0.12768814746316015
		 63 0.12740705547485087 64 0.12711717051989779 65 0.12681858119633316 66 0.12651139703844771
		 67 0.12619574910992704 68 0.12587179057290987 69 0.12553969722993086 70 0.12519966803560278
		 71 0.12485192557479274 72 0.12449671650395688 73 0.12413431195221736 74 0.12376500787869149
		 75 0.12338912538253388 76 0.1230070109620931 77 0.1226190367195672 78 0.12222560050751674
		 79 0.12182712601359824 80 0.12142406277989393 81 0.12101688615325212 82 0.12060609716310244
		 83 0.12019222232328097 84 0.11977581335449905 85 0.11935744682419525 86 0.1189377237006467
		 87 0.11851726881837288 88 0.11809673025204637 89 0.11767677859631132 90 0.11725810614915178
		 91 0.1168414259966829 92 0.11642747099750839 93 0.11601699266508003 94 0.1156107599468017
		 95 0.11520955789895704 96 0.11481418625688322 97 0.11442545790020209 98 0.11404419721329351
		 99 0.11367123834162141 100 0.11330742334494392 101 0.1129536002488819 102 0.11261062099678631
		 103 0.112279339304313 104 0.11196060841959909 105 0.11165527879243919 106 0.11136419565635958
		 107 0.11108819652800517 108 0.11082810862878445 109 0.11058474623422676 110 0.11035890795705849
		 111 0.11015137397051467 112 0.10996290317894819 113 0.10979423034331848 114 0.10964606316966408
		 115 0.10951907936918559 116 0.10941392369906189 117 0.10933120499362403 118 0.10927149319598595
		 119 0.10923531640069306 120 0.10922315791839288;
createNode animCurveTL -n "locator6_MKR_translateY";
	rename -uid "1844BAAE-4E48-69D3-2658-1BA0A93DEA34";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 0.12933321290050359 2 0.12933055582581576
		 3 0.12932268494432475 4 0.12930980890469279 5 0.12929221043210881 6 0.12927024219133598
		 7 0.12924432282783493 8 0.12921493317329591 9 0.1291826126027753 10 0.1291479555314281
		 11 0.12911160803956079 12 0.12907426461541649 13 0.12903666500572153 14 0.128999591164632
		 15 0.12896386429223861 16 0.12893034195431419 17 0.12889991527545497 18 0.12887350619820614
		 19 0.12885206480118883 20 0.12883656666962251 21 0.12882801031202162 22 0.12882741461717684
		 23 0.12883581634588759 24 0.12885426765220465 25 0.12888383362926747 26 0.12892558987510827
		 27 0.12898062007407918 28 0.12905001358984225 29 0.12913486306613353 30 0.12923626203178507
		 31 0.12935530250675398 32 0.12949307260617882 33 0.12965065413974675 34 0.12982912020392767
		 35 0.13002953276490714 36 0.13025294023031364 37 0.13050037500813494 38 0.1307728510514885
		 39 0.1310713613882164 40 0.13139687563456892 41 0.13175033749254961 42 0.13213266223082176
		 43 0.13254473414938361 44 0.1329874040285749 45 0.13346148656330536 46 0.13396775778376135
		 47 0.1345069524642033 48 0.13507976152184042 49 0.13568682940815513 50 0.13632875149543411
		 51 0.13700607146166477 52 0.13771927867736344 53 0.13846880559830954 54 0.13925502516858523
		 55 0.1400782482387315 56 0.14093872100427585 57 0.1418366224702976 58 0.14277206194813241
		 59 0.14374507659075075 60 0.14475562897376038 61 0.14580360472940257 62 0.14688881024133482
		 63 0.14801097040837763 64 0.14916972648580984 65 0.15036463401316291 66 0.15159516083782576
		 67 0.15286068524411478 68 0.15416049419777655 69 0.15549378171618611 70 0.15685964737476532
		 71 0.15825709496038032 72 0.15968503128267675 73 0.16114226515447561 74 0.16262750655247638
		 75 0.16413936596959144 76 0.16567635397028646 77 0.16723688096027445 78 0.16881925718187041
		 79 0.17042169294619314 80 0.17204229911323887 81 0.1736790878306389 82 0.17532997354163438
		 83 0.17699277427246907 84 0.17866521320901119 85 0.18034492057196749 86 0.18202943579953312
		 87 0.18371621004576322 88 0.18540260900231031 89 0.18708591605048641 90 0.18876333574986093
		 91 0.19043199766879937 92 0.19208896056148328 93 0.19373121689503281 94 0.19535569772939421
		 95 0.19695927795162038 96 0.19853878186511242 97 0.20009098913327394 98 0.20161264107587074
		 99 0.20310044731518651 100 0.20455109276783745 101 0.20596124497682577 102 0.20732756177711387
		 103 0.20864669928667268 104 0.20991532021358283 105 0.21113010246840003 106 0.21228774806958262
		 107 0.21338499232835662 108 0.21441861329796141 109 0.21538544147075855 110 0.21628236970523662
		 111 0.21710636336346467 112 0.21785447063807983 113 0.21852383304641498 114 0.21911169606789993
		 115 0.21961541989938971 116 0.22003249030161642 117 0.22036052950850571 118 0.22059730716964743
		 119 0.22074075129481485 120 0.22078895916800312;
createNode animCurveTU -n "locator6_MKR_enable";
	rename -uid "359EA2E9-47B0-DE4D-18E1-E3824A675B34";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 122 ".ktv[0:121]"  0 0 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1
		 95 1 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1
		 110 1 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1 121 0;
createNode animCurveTU -n "locator6_MKR_weight";
	rename -uid "B52A0845-43BF-BA9C-4168-68A46E7EEA70";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1 10 1
		 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1 27 1
		 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1 44 1
		 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1 61 1
		 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1
		 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1 95 1
		 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1 110 1
		 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1;
createNode animCurveTL -n "locator7_MKR_translateX";
	rename -uid "6C205321-4875-F708-5305-DA838D6DD32B";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 -0.0076807700880521801 2 -0.0076934888898060882
		 3 -0.0077313781405983217 4 -0.007794065080302448 5 -0.0078812126028860452 6 -0.0079925172874328876
		 7 -0.0081277075216393269 8 -0.0082865417103319405 9 -0.008468806562040021 10 -0.0086743154470949602
		 11 -0.0089029068211330942 12 -0.0091544427082583257 13 -0.0094288072384695054 14 -0.0097259052342683061
		 15 -0.01004566084167674 16 -0.010388016201153538 17 -0.010752930154165896 18 -0.011140376981406797
		 19 -0.011550345168872878 20 -0.011982836198223545 21 -0.012437863358042422 22 -0.012915450572805076
		 23 -0.013415631246527393 24 -0.013938447118242714 25 -0.014483947126609165 26 -0.015052186281100832
		 27 -0.015643224537384148 28 -0.016257125674627781 29 -0.016893956172622182 30 -0.017553784086734137
		 31 -0.018236677918849087 32 -0.018942705482590583 33 -0.019671932761238797 34 -0.020424422756909033
		 35 -0.021200234329681267 36 -0.021999421025516885 37 -0.022822029891934215 38 -0.023668100280561655
		 39 -0.024537662635836288 40 -0.025430737269265202 41 -0.026347333118825644 42 -0.02728744649324566
		 43 -0.028251059801067901 44 -0.029238140264580104 45 -0.030248638618873336 46 -0.03128248779647208
		 47 -0.032339601598180501 48 -0.033419873350983509 49 -0.03452317455404702 50 -0.035649353514078774
		 51 -0.036798233971527594 52 -0.037969613719324113 53 -0.039163263216101418 54 -0.040378924196064869
		 55 -0.041616308277929503 56 -0.042875095575585553 57 -0.044154933313408196 58 -0.04545543444937461
		 59 -0.046776176309418216 60 -0.048116699236697369 61 -0.049476505259723136 62 -0.050855056783541852
		 63 -0.052251775308428894 64 -0.053666040180796848 65 -0.055097187381274615 66 -0.056544508355150958
		 67 -0.058007248890611152 68 -0.059484608050414611 69 -0.060975737162882571 70 -0.06247973887825059
		 71 -0.063995666296636666 72 -0.065522522174032427 73 -0.067059258212877171 74 -0.068604774443899785
		 75 -0.070157918706012179 76 -0.071717486231125449 77 -0.073282219340798482 78 -0.074850807261660934
		 79 -0.076421886066538325 80 -0.077994038748167183 81 -0.079565795432313347 82 -0.081135633736995394
		 83 -0.082701979284366678 84 -0.084263206371623378 85 -0.085817638807079211 86 -0.087363550917286203
		 87 -0.088899168730767641 88 -0.090422671343582228 89 -0.091932192471554319 90 -0.093425822193564767
		 91 -0.094901608889825961 92 -0.096357561378553058 93 -0.097791651253880785 94 -0.099201815427283346
		 95 -0.10058595887411753 96 -0.10194195758623947 97 -0.10326766173092855 98 -0.10456089901561927
		 99 -0.10581947825715299 100 -0.10704119315345983 101 -0.1082238262547453 102 -0.10936515313038681
		 103 -0.11046294672685936 104 -0.11151498191110548 105 -0.11251904019282388 106 -0.11347291461821524
		 107 -0.11437441482675853 108 -0.11522137226161955 109 -0.11601164552331922 110 -0.11674312585529523
		 111 -0.11741374274901184 112 -0.1180214696552821 113 -0.11856432978748266 114 -0.11904040200137361
		 115 -0.11944782673526222 116 -0.11978481199331109 117 -0.12004963935385499 118 -0.12024066998368788
		 119 -0.12035635063840627 120 -0.12039521962804667;
createNode animCurveTL -n "locator7_MKR_translateY";
	rename -uid "FEAD6A69-47DA-06C5-80D7-0C972B5C823A";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 -0.088845273475847919 2 -0.088857441914633351
		 3 -0.088893635433450968 4 -0.088953332331513313 5 -0.089035942054381589 6 -0.089140808965986862
		 7 -0.089267215932683941 8 -0.089414387734810585 9 -0.089581494320188804 10 -0.089767653913062573
		 11 -0.089971935991106422 12 -0.090193364142341192 13 -0.090430918813078243 14 -0.090683539957329362
		 15 -0.09095012959752774 16 -0.091229554305822358 17 -0.091520647614701411 18 -0.091822212365215983
		 19 -0.092133023000629588 20 -0.092451827812911891 21 -0.092777351149105514 22 -0.093108295584246492
		 23 -0.093443344067168588 24 -0.093781162045220468 25 -0.094120399573617231 26 -0.094459693414859491
		 27 -0.094797669133385221 28 -0.095132943190352481 29 -0.095464125043192238 30 -0.095789819254318953
		 31 -0.096108627613137654 32 -0.096419151275236148 33 -0.096719992922405518 34 -0.097009758946876967
		 35 -0.097287061662906793 36 -0.097550521548590452 37 -0.097798769520500983 38 -0.098030449243487028
		 39 -0.098244219477670591 40 -0.098438756464385935 41 -0.098612756352498665 42 -0.098764937666206698
		 43 -0.098894043815103749 44 -0.09899884564691519 45 -0.099078144042958449 46 -0.099130772555985902
		 47 -0.099155600089666507 48 -0.099151533618540011 49 -0.099117520946834126 50 -0.099052553504078045
		 51 -0.098955669174967231 52 -0.098825955160436241 53 -0.0986625508663872 54 -0.098464650815981491
		 55 -0.098231507580869848 56 -0.09796243472614935 57 -0.097656809763284835 58 -0.097314077104621088
		 59 -0.096933751012521496 60 -0.096515418535551623 61 -0.096058742423520971 62 -0.095563464012553334
		 63 -0.095029406070757105 64 -0.094456475594423717 65 -0.093844666544078803 66 -0.093194062509094233
		 67 -0.092504839288976626 68 -0.091777267378859606 69 -0.09101171434617622 70 -0.090208647084941029
		 71 -0.08936863393357275 72 -0.088492346641713404 73 -0.08758056217106247 74 -0.086634164314861539
		 75 -0.08565414512032471 76 -0.084641606098019073 77 -0.0835977592019852 78 -0.082523927564218613
		 79 -0.081421545967049813 80 -0.080292161036945919 81 -0.079137431143321391 82 -0.077959125986099664
		 83 -0.076759125856007249 84 -0.075539420551916869 85 -0.074302107939983597 86 -0.073049392139862779
		 87 -0.071783581323915713 88 -0.070507085116068624 89 -0.069222411577830434 90 -0.067932163769939102
		 91 -0.06663903587917247 92 -0.065345808901043578 93 -0.064055345870393854 94 -0.062770586633289271
		 95 -0.06149454215514244 96 -0.060230288361593665 97 -0.058980959510397668 98 -0.057749741094383134
		 99 -0.056539862277462327 100 -0.05535458786766434 101 -0.054197209833255877 102 -0.053071038370180013
		 103 -0.051979392531270152 104 -0.050925590430013601 105 -0.049912939033986969 106 -0.048944723565500226
		 107 -0.048024196529438623 108 -0.047154566390770536 109 -0.046338985926697829 110 -0.045580540280938275
		 111 -0.044882234750154348 112 -0.044246982335047536 113 -0.043677591091128676 114 -0.043176751316628237
		 115 -0.042747022617424413 116 -0.042390820891214431 117 -0.042110405275430862 118 -0.041907865105603292
		 119 -0.041785106932937632 120 -0.041743841651868507;
createNode animCurveTU -n "locator7_MKR_enable";
	rename -uid "EA67B869-4487-69D1-3DF8-93925BDF95FF";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 122 ".ktv[0:121]"  0 0 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1
		 95 1 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1
		 110 1 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1 121 0;
createNode animCurveTU -n "locator7_MKR_weight";
	rename -uid "1E16807D-4CA3-4C63-86F3-2E915D4ACC97";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1 10 1
		 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1 27 1
		 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1 44 1
		 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1 61 1
		 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1
		 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1 95 1
		 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1 110 1
		 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1;
createNode animCurveTL -n "locator8_MKR_translateX";
	rename -uid "C9A4D7FB-4F22-9384-D1EB-A59EA3927644";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 0.17783820872640455 2 0.17784121292779564
		 3 0.17785015090177592 4 0.17786490073927896 5 0.1778853278149064 6 0.17791128546001034
		 7 0.17794261559385016 8 0.17797914931657643 9 0.1780207074675324 10 0.17806710115212288
		 11 0.17811813224028505 12 0.17817359383939813 13 0.17823327074428441 14 0.17829693986680506
		 15 0.17836437064738497 16 0.17843532545068952 17 0.1785095599475347 18 0.17858682348501098
		 19 0.17866685944669536 20 0.17874940560473607 21 0.17883419446550419 22 0.17892095361043159
		 23 0.17900940603358495 24 0.17909927047745167 25 0.17919026176835651 26 0.17928209115286986
		 27 0.1793744666365118 28 0.1794670933260003 29 0.1795596737762527 30 0.17965190834328637
		 31 0.17974349554413027 32 0.17983413242480217 33 0.17992351493736414 34 0.18001133832702099
		 35 0.18009729753017434 36 0.18018108758429863 37 0.18026240405044947 38 0.18034094344916629
		 39 0.18041640371046341 40 0.18048848463855505 41 0.18055688839188855 42 0.18062131997899222
		 43 0.18068148777057269 44 0.18073710402822429 45 0.18078788545001812 46 0.18083355373316889
		 47 0.1808738361538641 48 0.1809084661642586 49 0.18093718400652081 50 0.1809597373437114
		 51 0.1809758819071513 52 0.18098538215981852 53 0.18098801197517178 54 0.18098355533067245
		 55 0.18097180701511884 56 0.18095257334876513 57 0.1809256729150317 58 0.18089093730245431
		 59 0.18084821185534472 60 0.180797356431463 61 0.18073824616481471 62 0.18067077223150796
		 63 0.18059484261640468 64 0.18051038287811827 65 0.18041733690970396 66 0.18031566769219376
		 67 0.18020535803793103 68 0.18008641132046155 69 0.17995885218753471 70 0.17982272725358572
		 71 0.17967810576787169 72 0.17952508025425429 73 0.17936376711844892 74 0.17919430721838503
		 75 0.17901686639318015 76 0.17883163594607021 77 0.17863883307652684 78 0.1784387012566695
		 79 0.17823151054699271 80 0.17801755784635565 81 0.1777971670711308 82 0.17757068925838726
		 83 0.17733850258798134 84 0.17710101231846553 85 0.17685865063178652 86 0.1766118763818344
		 87 0.17636117474204172 88 0.17610705674739857 89 0.17585005872644244 90 0.17559074161904198
		 91 0.17532969017606648 92 0.17506751203736204 93 0.17480483668482427 94 0.17454231426776834
		 95 0.1742806142982517 96 0.17402042421449693 97 0.17376244781111239 98 0.17350740353537719
		 99 0.17325602264949125 100 0.17300904725934618 101 0.17276722821107471 102 0.17253132285737571
		 103 0.17230209269637553 104 0.17208030088658743 105 0.17186670964236095 106 0.1716620775150578
		 107 0.17146715656605849 108 0.17128268943859637 109 0.17110940633629235 110 0.17094802191718084
		 111 0.17079923211289572 112 0.17066371088358512 113 0.17054210691999894 114 0.17043504030503875
		 115 0.17034309914790646 116 0.17026683620476402 117 0.17020676550058411 118 0.17016335896756907
		 119 0.17013704311616684 120 0.17012819575529403;
createNode animCurveTL -n "locator8_MKR_translateY";
	rename -uid "89C7D641-4935-8105-F020-3FB0DEBB6A72";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 -0.048901358264424266 2 -0.048916052487658179
		 3 -0.04895976927628487 4 -0.049031909878736069 5 -0.049131811883595 6 -0.049258752705108433
		 7 -0.049411952894220623 8 -0.049590579289430448 9 -0.049793748020805828 10 -0.05002052737960011
		 11 -0.050269940565111804 12 -0.050540968319681912 13 -0.050832551462061448 14 -0.051143593328740078
		 15 -0.051472962132286693 16 -0.05181949324521018 17 -0.052181991417385776 18 -0.052559232934649258
		 19 -0.052949967725752167 20 -0.053352921424509092 21 -0.053766797393608734 22 -0.054190278716252649
		 23 -0.054622030161471213 24 -0.055060700128700679 25 -0.055504922576930849 26 -0.055953318943481323
		 27 -0.056404500057231521 28 -0.056857068050894743 29 -0.057309618276707774 30 -0.057760741229684387
		 31 -0.058209024482374028 32 -0.05865305463485021 33 -0.059091419283444302 34 -0.059522709011523456
		 35 -0.059945519405393111 36 -0.060358453098191656 37 -0.060760121844399217 38 -0.061149148627364314
		 39 -0.061524169801993656 40 -0.0618838372744972 41 -0.062226820720821197 42 -0.062551809845102668
		 43 -0.062857516679205583 44 -0.063142677924071078 45 -0.063406057333299404 46 -0.063646448139030587
		 47 -0.063862675519836321 48 -0.064053599109951842 49 -0.064218115548781318 50 -0.064355161069191202
		 51 -0.064463714122670712 52 -0.06454279803897961 53 -0.06459148371743112 54 -0.064608892346454394
		 55 -0.064594198147578497 56 -0.064546631139429378 57 -0.064465479916795465 58 -0.064350094439242944
		 59 -0.064199888823173401 60 -0.064014344130626344 61 -0.063793011147522949 62 -0.063535513143407774
		 63 -0.063241548604144882 64 -0.062910893928369349 65 -0.062543406077870678 66 -0.062139025171447204
		 67 -0.061697777011142541 68 -0.06121977552914698 69 -0.060705225143043606 70 -0.060154423006481161
		 71 -0.059567761141783249 72 -0.058945728440459588 73 -0.058288912517063973 74 -0.057598001401371057
		 75 -0.056873785053403902 76 -0.056117156685450753 77 -0.055329113874883762 78 -0.054510759451305846
		 79 -0.053663302141345848 80 -0.052788056954285956 81 -0.051886445291638439 82 -0.050959994763813632
		 83 -0.050010338697136669 84 -0.04903921531467248 85 -0.04804846657462708 86 -0.04704003665051526
		 87 -0.046015970037795062 88 -0.044978409272323661 89 -0.043929592246738092 90 -0.042871849111751681
		 91 -0.041807598750358721 92 -0.040739344814075262 93 -0.039669671311613919 94 -0.038601237741770156
		 95 -0.037536773763829911 96 -0.03647907340045875 97 -0.03543098876980505 98 -0.034395423345457865
		 99 -0.03337532474492344 100 -0.03237367704941696 101 -0.031393492660024669 102 -0.030437803697640986
		 103 -0.029509652956532573 104 -0.028612084423925266 105 -0.02774813338062132 106 -0.026920816100337752
		 107 -0.026133119168198216 108 -0.02538798844158846 109 -0.02468831767940205 110 -0.024036936868522429
		 111 -0.023436600279219122 112 -0.022889974283939629 113 -0.02239962497675474 114 -0.021968005633430487
		 115 -0.02159744405475833 116 -0.021290129838324234 117 -0.02104810162634535 118 -0.02087323437952382
		 119 -0.02076722672901099 120 -0.020731588460575989;
createNode animCurveTU -n "locator8_MKR_enable";
	rename -uid "094BE352-46EE-AB22-5A35-DB9886C575E0";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 122 ".ktv[0:121]"  0 0 1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1
		 10 1 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1
		 27 1 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1
		 44 1 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1
		 61 1 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1
		 78 1 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1
		 95 1 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1
		 110 1 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1 121 0;
createNode animCurveTU -n "locator8_MKR_weight";
	rename -uid "25F83EF3-4AE0-D4D6-6F50-92AA6BE69A03";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1 10 1
		 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1 27 1
		 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1 44 1
		 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1 61 1
		 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1
		 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1 95 1
		 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1 110 1
		 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1;
createNode expression -n "expression1";
	rename -uid "0B5942FD-422C-A736-B81D-5BA4014C836E";
	setAttr -k on ".nds";
	setAttr ".ixp" -type "string" ".O[0]=frame";
createNode shadingEngine -n "geom:lambert2SG";
	rename -uid "B287C0AB-4351-EFC5-4290-3F9F3BB7D4AE";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
	setAttr -s 2 ".gn";
createNode materialInfo -n "geom:materialInfo1";
	rename -uid "725F0C14-496A-6D0C-638A-EEAA621013B9";
createNode groupId -n "geom:groupId1";
	rename -uid "F13920A5-4787-4228-86DF-1EA3F0EC245D";
	setAttr ".ihi" 0;
createNode groupId -n "geom:groupId2";
	rename -uid "B89404FB-4630-81CC-6137-E0922855B1DA";
	setAttr ".ihi" 0;
createNode lambert -n "geom:lambert2SG1";
	rename -uid "06DF5DF9-4677-C098-0686-2DB0170EF2A9";
	setAttr ".c" -type "float3" 1 0.5 0.5 ;
createNode shadingEngine -n "geom:lambert4SG";
	rename -uid "E00BA0AE-4836-CA2C-9C5F-1F8205752989";
	setAttr ".ihi" 0;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
	setAttr -s 2 ".gn";
createNode materialInfo -n "geom:materialInfo2";
	rename -uid "8987B058-48A5-6523-6354-B5ACC7AD6093";
createNode groupId -n "geom:groupId3";
	rename -uid "095A3D1D-4801-AE42-E026-75A568A97A72";
	setAttr ".ihi" 0;
createNode groupId -n "geom:groupId4";
	rename -uid "1D9ABEBA-4EF2-4149-4A1B-1091B3018F81";
	setAttr ".ihi" 0;
createNode lambert -n "geom:lambert4SG1";
	rename -uid "06046018-49EA-029A-1F23-BDAEE490622D";
	setAttr ".c" -type "float3" 0.5 0.5 1 ;
createNode shadingEngine -n "geom:lambert5SG";
	rename -uid "C417979F-4618-B4C2-344D-169B36DE1A41";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "geom:materialInfo3";
	rename -uid "AB51A62A-402E-3AF6-539E-788031B0C534";
createNode groupId -n "geom:groupId5";
	rename -uid "DFA8249F-4C5A-9EE8-2F6B-27BF9287F993";
	setAttr ".ihi" 0;
createNode lambert -n "geom:lambert5SG1";
	rename -uid "48FA473C-4F0E-491F-9819-B0898E0CB499";
	setAttr ".c" -type "float3" 0.5 1 0.5 ;
createNode shadingEngine -n "geom:lambert3SG";
	rename -uid "3780D437-4715-7610-E05A-F9A07D4A81CD";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "geom:materialInfo4";
	rename -uid "26594D25-42FF-0B59-12C5-5B87B7FDF2EE";
createNode groupId -n "geom:groupId6";
	rename -uid "E9519E3C-4563-D9FE-41F2-769EA6F1EA6A";
	setAttr ".ihi" 0;
createNode lambert -n "geom:lambert3SG1";
	rename -uid "1DB098CD-40E4-1E98-7C36-D69C4C04E88C";
createNode animCurveTL -n "pCube1_translateX";
	rename -uid "43B873C1-43B6-E818-9365-6D9B3EBAA7EE";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 -1.584477125235297e-005 2 0.00083173291386228572
		 3 0.0035032078536520925 4 0.0076651946983805645 5 0.013568778787953801 6 0.021088475480527061
		 7 0.03019920713000436 8 0.040871731904645825 9 0.053076918511935668 10 0.066784138703340337
		 11 0.081968462922053689 12 0.098596405050116298 13 0.11664026968975273 14 0.13607077406666712
		 15 0.15685876587822631 16 0.17897503595865802 17 0.20239040541492209 18 0.22707569388456669
		 19 0.25300170136901035 20 0.28013921318811041 21 0.30845904890269843 22 0.33793202587023446
		 23 0.36852893425909222 24 0.40022059278269878 25 0.43297780833687938 26 0.46677137592899859
		 27 0.50157210819586728 28 0.53735081301406573 29 0.57407831100334128 30 0.61172539685772931
		 31 0.65026288011689393 32 0.68966156086368235 33 0.72989225914818523 34 0.77092577517156735
		 35 0.8127329284653384 36 0.85528449864229728 37 0.89855132212272348 38 0.94250419244387285
		 39 0.9871139251155564 40 1.0323513211263979 41 1.0781871694589023 42 1.1245923157983182
		 43 1.1715375256908078 44 1.218993645317209 45 1.266931429788561 46 1.3153217197959095
		 47 1.3641353049310871 48 1.4133429808869953 49 1.4629155563642671 50 1.512823833750164
		 51 1.5630386087971417 52 1.613530663158818 53 1.6642708516269253 54 1.7152299310850749
		 55 1.7663787381635574 56 1.8176880490764422 57 1.8691287088357658 58 1.9206715239490786
		 59 1.9722873313520357 60 2.0239469590396761 61 2.0756212493396462 62 2.1272810324050111
		 63 2.1788972115715595 64 2.2304405914256318 65 2.2818821441662833 66 2.33319265805692
		 67 2.3843431132593436 68 2.4353043828851755 69 2.4860474123558962 70 2.5365431318703879
		 71 2.5867624078618174 72 2.6366763097655355 73 2.686255657757763 74 2.7354714938533009
		 75 2.7842946117275522 76 2.8326961534251356 77 2.8806468437057187 78 2.9281177493271513
		 79 2.9750796853665364 80 3.0215036565748594 81 3.0673603116259569 82 3.1126207555782135
		 83 3.1572556230505726 84 3.2012359501271956 85 3.2445322556755416 86 3.2871153246293314
		 87 3.328955994758672 88 3.3700250244347814 89 3.4102929750620139 90 3.4497304600197274
		 91 3.4883082765315163 92 3.5259969601585457 93 3.5627669900239862 94 3.5985889680465468
		 95 3.6334337282951812 96 3.6672715840429775 97 3.7000732228941882 98 3.7318088997298977
		 99 3.7624497293035133 100 3.7919658595614893 101 3.8203277780455678 102 3.8475064485908863
		 103 3.8734722134469619 104 3.8981956596318019 105 3.9216474103930894 106 3.9437982825250266
		 107 3.9646184274012559 108 3.9840791128505444 109 4.0021506162629397 110 4.0188037150052152
		 111 4.0340092283992801 112 4.0477377022079253 113 4.059959802161929 114 4.070646628506057
		 115 4.0797685589786363 116 4.087296264730754 117 4.0932010082504062 118 4.0974530878812514
		 119 4.1000235156155878 120 4.1008829166830285;
	setAttr -s 120 ".kit[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2;
	setAttr -s 120 ".kot[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2;
createNode animCurveTL -n "pCube1_translateY";
	rename -uid "7B61763B-43E2-6263-8601-9C8D2512AE69";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 -6.9676100385418921e-006 2 -0.0010594331644134822
		 3 -0.0041409513023614218 4 -0.0093390738102231852 5 -0.016496601582184023 6 -0.025623667606188946
		 7 -0.036681854947869685 8 -0.049635750878450985 9 -0.064449895390474785 10 -0.081088917925846271
		 11 -0.099517219490759451 12 -0.11969954014324025 13 -0.14160036362195974 14 -0.16518429239272173
		 15 -0.19041587573237409 16 -0.217259688092373 17 -0.24568028667888586 18 -0.27564223754112005
		 19 -0.30711010582763681 20 -0.34004846840898517 21 -0.37442188789517084 22 -0.41019492375390498
		 23 -0.44733215248965558 24 -0.48579813312324238 25 -0.525557433322971 26 -0.56657462381988721
		 27 -0.60881426896959534 28 -0.65224093537552574 29 -0.69681918479228944 30 -0.74251358667175771
		 31 -0.78928870674617957 32 -0.83710911668129373 33 -0.88593937636205211 34 -0.93574405508010483
		 35 -0.9864877157276517 36 -1.0381349351734079 37 -1.0906502698421183 38 -1.1439982906262776
		 39 -1.1981435624353478 40 -1.2530506531050873 41 -1.3086841388362827 42 -1.3650085711569215
		 43 -1.4219885304210851 44 -1.4795885706355625 45 -1.5377732746929285 46 -1.5965071967258639
		 47 -1.6557549075638589 48 -1.7154809735666883 49 -1.7756499561267882 50 -1.8362264187856556
		 51 -1.897174924190379 52 -1.9584600382704167 53 -2.0200463041198922 54 -2.0818982855819734
		 55 -2.1439805297709698 56 -2.2062575920108509 57 -2.2686940111955818 58 -2.331254328626589
		 59 -2.3939030782182318 60 -2.4566047962693829 61 -2.5193240082482888 62 -2.5820252460434561
		 63 -2.644673013207635 64 -2.7072318512978888 65 -2.7696662430743779 66 -2.8319407352529038
		 67 -2.8940198051152297 68 -2.9558679840303181 69 -3.0174497658847068 70 -3.078729664567295
		 71 -3.1396722069611811 72 -3.2002418763320124 73 -3.260403232205888 74 -3.3201207587247326
		 75 -3.3793590420916515 76 -3.4380825610316297 77 -3.4962559213378568 78 -3.5538436436749068
		 79 -3.6108103322962823 80 -3.6671205079738374 81 -3.7227388341489105 82 -3.7776298648915136
		 83 -3.8317582253814186 84 -3.8850885064206326 85 -3.937585392411072 86 -3.9892135462354732
		 87 -4.0399375501853143 88 -4.089722059396661 89 -4.1385317963367623 90 -4.1863314265626252
		 91 -4.233085552126977 92 -4.2787588964871324 93 -4.3233161325415246 94 -4.3667219973592584
		 95 -4.4089410145998835 96 -4.4499379932616021 97 -4.4896774964787616 98 -4.5281242953553296
		 99 -4.5652429297828325 100 -4.6009981231049393 101 -4.6353545025781182 102 -4.6682766711533423
		 103 -4.6997292669890465 104 -4.7296769555458864 105 -4.7580842920426871 106 -4.7849158720681206
		 107 -4.8101363766171064 108 -4.8337102938660683 109 -4.8556022642860217 110 -4.8757768722354662
		 111 -4.8941986389470022 112 -4.9108322060471021 113 -4.9256420890667227 114 -4.938592849875528
		 115 -4.9496490740500256 116 -4.9587753856736043 117 -4.9659361857004143 118 -4.9710961621320706
		 119 -4.9742198822386987 120 -4.9752718344440545;
	setAttr -s 120 ".kit[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2;
	setAttr -s 120 ".kot[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2;
createNode animCurveTL -n "pCube1_translateZ";
	rename -uid "7D5AA6E3-45AE-4321-0DB7-409F8988B6D4";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 -1.1702588277569948e-005 2 -0.0029658110674479518
		 3 -0.011631478583085124 4 -0.026122520419793023 5 -0.046158130719453294 6 -0.07170112323999718
		 7 -0.10264855276843998 8 -0.13890128302211549 9 -0.1803601127918934 10 -0.22692641253467849
		 11 -0.27849944595336112 12 -0.33498163521739072 13 -0.39627324863038671 14 -0.46227517697903003
		 15 -0.53288822950677595 16 -0.60801325372422821 17 -0.6875510753263947 18 -0.7714025245682653
		 19 -0.85946843796302352 20 -0.95164966794846495 21 -1.0478470407531613 22 -1.1479613864058531
		 23 -1.251893551290145 24 -1.3595443640573326 25 -1.4708146597606371 26 -1.5856052811896559
		 27 -1.7038170622100237 28 -1.8253508366343922 29 -1.9501074334483137 30 -2.077987694984587
		 31 -2.2088924541231982 32 -2.3427225526274875 33 -2.4793788190144119 34 -2.6187620924144461
		 35 -2.7607732012238095 36 -2.9053129986133439 37 -3.052282304094919 38 -3.2015819616066259
		 39 -3.3531128029554131 40 -3.5067756680259197 41 -3.6624714082802163 42 -3.8201008340592617
		 43 -3.9795648078005565 44 -4.1407641454350603 45 -4.3035997124744734 46 -4.4679723272725251
		 47 -4.6337828313057594 48 -4.8009320685711003 49 -4.9693208699097946 50 -5.1388500681927747
		 51 -5.3094204983343563 52 -5.4809330019276841 53 -5.653288368891193 54 -5.8263874485589087
		 55 -6.0001310366398704 56 -6.1744199575435896 57 -6.3491549918926324 58 -6.5242369348524463
		 59 -6.6995665598947145 60 -6.8750446339441957 61 -7.050571911148066 62 -7.2260491524148431
		 63 -7.4013770511980415 64 -7.5764563705945847 65 -7.7511877545163745 66 -7.9254719659047073
		 67 -8.099209623178325 68 -8.2723014387780491 69 -8.444648044138729 70 -8.6161501047242393
		 71 -8.7867083111023341 72 -8.9562232263480386 73 -9.1245955967595087 74 -9.291725988709878
		 75 -9.4575152009773706 76 -9.6218637465513428 77 -9.784672464030443 78 -9.945841971759501
		 79 -10.105273057482188 80 -10.262866393356616 81 -10.418522919962349 82 -10.572143273019543
		 83 -10.723628442940901 84 -10.872879160409841 85 -11.019796466317796 86 -11.164281358861908
		 87 -11.306234689692966 88 -11.445557418628344 89 -11.582150753479141 90 -11.715915730151393
		 91 -11.846753341810455 92 -11.974564788199865 93 -12.099251246793601 94 -12.220713908029175
		 95 -12.338853755971705 96 -12.453572162416322 97 -12.564770195594219 98 -12.672349237123044
		 99 -12.776210164316021 100 -12.876254370255797 101 -12.972383092594223 102 -13.064497247920732
		 103 -13.15249814301786 104 -13.236286928806267 105 -13.315764697008026 106 -13.390832418531087
		 107 -13.461391456853452 108 -13.527342579941708 109 -13.588586953108807 110 -13.645025611091873
		 111 -13.696559516993318 112 -13.743089695914904 113 -13.784517195915827 114 -13.820742717194859
		 115 -13.85166748829745 116 -13.877192454955752 117 -13.897218262748018 118 -13.91164609015831
		 119 -13.920376773694839 120 -13.923311223337404;
	setAttr -s 120 ".kit[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2;
	setAttr -s 120 ".kot[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2;
createNode animCurveTA -n "pCube1_rotateX";
	rename -uid "A3FD5FB8-4A71-22A8-B072-6186E6F9935D";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 -1.3053457085625058e-005 2 -0.0053175937032495721
		 3 -0.021042796164243188 4 -0.047420110459737715 5 -0.083760357321720824 6 -0.13004966715026245
		 7 -0.18606134237289182 8 -0.25157487608447465 9 -0.32636322631806991 10 -0.41017564428192899
		 11 -0.50282708687163324 12 -0.60401966165764132 13 -0.71352157735714328 14 -0.83107831249044251
		 15 -0.95643026649022245 16 -1.0893131753820529 17 -1.229458273240047 18 -1.3765926237715214
		 19 -1.5304391141317921 20 -1.6907169089383662 21 -1.857141547091532 22 -2.0294250694721612
		 23 -2.207276634241091 24 -2.3904022503504119 25 -2.5785055117308771 26 -2.7712876123947674
		 27 -2.9684477337648585 28 -3.1696833092779446 29 -3.3746903315314585 30 -3.5831637024171794
		 31 -3.7947975259530846 32 -4.009285574682294 33 -4.2263214139946674 34 -4.4455989932688578
		 35 -4.6668128709468473 36 -4.8896586710843168 37 -5.113833362745221 38 -5.3390357802599002
		 39 -5.5649668618917554 40 -5.7913301684273222 41 -6.0178322999204923 42 -6.2441830048563363
		 43 -6.4700959264908189 44 -6.6952886722163933 45 -6.9194835593848225 46 -7.1424075911205094
		 47 -7.363793146297545 48 -7.5833780820228069 49 -7.8009063441567275 50 -8.0161280874869316
		 51 -8.2288001428135367 52 -8.4386863752025949 53 -8.6455579774283891 54 -8.8491935166172002
		 55 -9.0493797692465723 56 -9.2459115790981343 57 -9.4385923363777522 58 -9.627234088030999
		 59 -9.811658012698258 60 -9.9916945340756378 61 -10.167183617216905 62 -10.337974918045466
		 63 -10.503928066876984 64 -10.664913180886677 65 -10.820810167457925 66 -10.971510324981594
		 67 -11.116914779708344 68 -11.256936716757316 69 -11.391499555583119 70 -11.52053843432186
		 71 -11.64399983550755 72 -11.761841830870143 73 -11.874034491086377 74 -11.98055907578747
		 75 -12.081409484770143 76 -12.176590910832939 77 -12.266121637663632 78 -12.350031080760946
		 79 -12.428361758884582 80 -12.501167453560619 81 -12.568515241524652 82 -12.630483884568834
		 83 -12.687163390146502 84 -12.73865708284135 85 -12.785080968128096 86 -12.826560927208918
		 87 -12.863235128408608 88 -12.89525356232512 89 -12.922777324022976 90 -12.945978714222832
		 91 -12.965038802786701 92 -12.980150755256579 93 -12.991516410418081 94 -12.99934817767036
		 95 -13.003862837310308 96 -13.005291130776776 97 -13.003865374749523 98 -12.999829108250648
		 99 -12.993427185195056 100 -12.984912881707739 101 -12.974541226245929 102 -12.96256999463686
		 103 -12.949259534262712 104 -12.9348714536378 105 -12.919663494829082 106 -12.903895477157432
		 107 -12.887822341049304 108 -12.871692054889959 109 -12.855750989577874 110 -12.840234670115997
		 111 -12.825369625884566 112 -12.811374137959286 113 -12.79845046490699 114 -12.786791235854174
		 115 -12.776570717678354 116 -12.767948112462177 117 -12.761058526417665 118 -12.756025102927069
		 119 -12.752943668120247 120 -12.751885534757117;
	setAttr -s 120 ".kit[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2;
	setAttr -s 120 ".kot[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2;
createNode animCurveTA -n "pCube1_rotateY";
	rename -uid "DC0A2264-4C54-3DA2-C113-D29778C3CEA0";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 2.641579686705354e-006 2 0.0039136283707217508
		 3 0.015655899172177107 4 0.034996391158416774 5 0.061956954951001245 6 0.096396639043127397
		 7 0.1382666867479172 8 0.18751428673601792 9 0.24409799636111656 10 0.30803170503348209
		 11 0.37915938129932553 12 0.4576028949815259 13 0.54331223135293794 14 0.63628908461792122
		 15 0.73654096376079414 16 0.84408049164256282 17 0.95892437220476867 18 1.0810925337755664
		 19 1.2106075309968247 20 1.3474934248413928 21 1.4917751723508295 22 1.6434778463778648
		 23 1.8026257189079207 24 1.9692417990861686 25 2.1433468895190555 26 2.3249590706472172
		 27 2.5140928630690889 28 2.7107587612227406 29 2.9149625355564024 30 3.1267047166121982
		 31 3.3459800505981128 32 3.5727768391033852 33 3.8070766550999497 34 4.0488537568665732
		 35 4.298074688226011 36 4.5546979783336852 37 4.81867356727704 38 5.0899427194671238
		 39 5.3684376047334874 40 5.6540810768185343 41 5.9467862964235954 42 6.2464568261312614
		 43 6.5529862852251126 44 6.8662581515239998 45 7.1861459094599791 46 7.5125126588387383
		 47 7.8452114085178488 48 8.1840848794585597 49 8.5289655223988152 50 8.8796756895318971
		 51 9.2360276759776383 52 9.5978237823105594 53 9.9648563265128551 54 10.336908341835681
		 55 10.71375297520691 56 11.095154417976318 57 11.480867553331976 58 11.870638709700131
		 59 12.264205497462722 60 12.661297465200535 61 13.061636138691545 62 13.464935442096078
		 63 13.870902102821335 64 14.279235800458704 65 14.689629692663416 66 15.10177075686795
		 67 15.515340345585946 68 15.930013751528131 69 16.345461964827354 70 16.761350792834723
		 71 17.177342368487476 72 17.593094254534233 73 18.008260875098493 74 18.422494348084296
		 75 18.83544274634934 76 19.246752951090215 77 19.656070061643632 78 20.063036861151147
		 79 20.467296101401125 80 20.868489083244604 81 21.266257909991314 82 21.660243322326284
		 83 22.050087857016077 84 22.435433432574296 85 22.815924852666758 86 23.191206591699462
		 87 23.560926262257961 88 23.924732131821205 89 24.2822756032221 90 24.63321122892625
		 91 24.977195019205194 92 25.313885784830397 93 25.642948644234401 94 25.964047146742587
		 95 26.276851109674528 96 26.581033724907194 97 26.876271102959208 98 27.162245005996724
		 99 27.438637253737081 100 27.705136208984577 101 27.961434334625324 102 28.207223933737854
		 103 28.442205417317627 104 28.666081200820564 105 28.878554060668989 106 29.079334363995596
		 107 29.26813459139202 108 29.444665171698791 109 29.608647249956785 110 29.759797532250303
		 111 29.897837597873213 112 30.022492415046532 113 30.133487195327838 114 30.230548104855604
		 115 30.313405130132796 116 30.381787246961157 117 30.435424042241035 118 30.474049867684432
		 119 30.49739319011255 120 30.505190721239092;
	setAttr -s 120 ".kit[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2;
	setAttr -s 120 ".kot[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2;
createNode animCurveTA -n "pCube1_rotateZ";
	rename -uid "FBD1EED6-4340-C2AE-0571-8F83BE51841D";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 1.4227133401642522e-005 2 -0.002392862241261195
		 3 -0.0094410035419930406 4 -0.021055627752646838 5 -0.03726599591948989 6 -0.057951471631474252
		 7 -0.08306530432972746 8 -0.11255642965410684 9 -0.14637807320449001 10 -0.18449824309377716
		 11 -0.22684528319305544 12 -0.27341595314731482 13 -0.32416679995114672 14 -0.37906793845305653
		 15 -0.4380921054638266 16 -0.50121427595069079 17 -0.56841139656242212 18 -0.63966206417380644
		 19 -0.71494632958129634 20 -0.7942452369962375 21 -0.87754070903055825 22 -0.96481514947499158
		 23 -1.0560511009830622 24 -1.1512310526718994 25 -1.2503370353217753 26 -1.3533503249529428
		 27 -1.4602511672628293 28 -1.5710184007031402 29 -1.6856292085034879 30 -1.8040587703032018
		 31 -1.926279910977565 32 -2.0522628476804168 33 -2.1819748807810049 34 -2.3153800724488649
		 35 -2.4524389476057968 36 -2.5931082228445419 37 -2.7373405565124882 38 -2.8850842842444808
		 39 -3.0362831169225561 40 -3.1908759794475525 41 -3.3487967070360876 42 -3.5099739964312495
		 43 -3.6743310855018518 44 -3.8417856618674473 45 -4.0122496917043478 46 -4.1856293816060965
		 47 -4.3618249907731919 48 -4.5407308784420932 49 -4.7222353701246922 50 -4.9062208304561095
		 51 -5.0925636259990448 52 -5.2811342136552639 53 -5.4717971498528071 54 -5.6644113675646501
		 55 -5.8588300867632581 56 -6.0549011493347376 57 -6.2524670948039196 58 -6.4513655132119565
		 59 -6.6514291912848984 60 -6.8524863866306482 61 -7.0543612090378893 62 -7.2568738832202397
		 63 -7.4598412123856619 64 -7.6630766977228726 65 -7.8663912749195815 66 -8.0695934704095098
		 67 -8.2724901254249978 68 -8.4748863060154935 69 -8.6765865285125621 70 -8.8773946466206901
		 71 -9.0771145637004125 72 -9.2755508736809187 73 -9.4725089790346111 74 -9.6677962546075804
		 75 -9.8612215825063316 76 -10.052597101699041 77 -10.241737639860776 78 -10.428461843623086
		 79 -10.612592274266273 80 -10.793956612168261 81 -10.972387075144232 82 -11.147721399398801
		 83 -11.319804024389052 84 -11.488484805204388 85 -11.65362075551262 86 -11.8150757055366
		 87 -11.972721486748574 88 -12.126436764889656 89 -12.276107992376854 90 -12.421630417501099
		 91 -12.562907134734996 92 -12.699848776611377 93 -12.832375258702658 94 -12.960412533679463
		 95 -13.083897746285075 96 -13.202772943164728 97 -13.316990083119151 98 -13.426506662708622
		 99 -13.531288201408262 100 -13.631306288558919 101 -13.726539444011223 102 -13.816969580428301
		 103 -13.902586285426864 104 -13.98338125361885 105 -14.059349479114653 106 -14.130490414801406
		 107 -14.196803567146794 108 -14.258289300735424 109 -14.314949446815747 110 -14.366782088510513
		 111 -14.413785680395694 112 -14.455954088704832 113 -14.493277679579725 114 -14.525740842090178
		 115 -14.55332269366434 116 -14.575992447807444 117 -14.593713678211355 118 -14.606439597159406
		 119 -14.614110999581973 120 -14.616660712558716;
	setAttr -s 120 ".kit[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2;
	setAttr -s 120 ".kot[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2;
createNode objectSet -n "collection1";
	rename -uid "89BFF4AE-454C-6075-6D49-E59BE1C6385A";
	addAttr -ci true -sn "solver_list" -ln "solver_list" -dt "string";
	addAttr -ci true -sn "solver_step_list" -ln "solver_step_list" -dt "string";
	addAttr -ci true -sn "override_current_frame" -ln "override_current_frame" -min 
		0 -max 1 -at "bool";
	addAttr -ci true -sn "object_toggle_camera" -ln "object_toggle_camera" -dv 1 -min 
		0 -max 1 -at "bool";
	addAttr -ci true -sn "object_toggle_marker" -ln "object_toggle_marker" -dv 1 -min 
		0 -max 1 -at "bool";
	addAttr -ci true -sn "object_toggle_bundle" -ln "object_toggle_bundle" -min 0 -max 
		1 -at "bool";
	setAttr ".ihi" 0;
	setAttr -s 12 ".dsm";
	setAttr -s 9 ".dnsm";
	setAttr -l on ".solver_list" -type "string" (
		"[{\"enabled\": true, \"frame_list\": [{\"number\": 1, \"tags\": [\"normal\"]}, {\"number\": 30, \"tags\": [\"normal\"]}, {\"number\": 60, \"tags\": [\"normal\"]}, {\"number\": 90, \"tags\": [\"normal\"]}, {\"number\": 120, \"tags\": [\"normal\"]}], \"name\": \"fa004350-c6c7-4140-9a91-9a2cd57a120f\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 1, \"tags\": [\"normal\"]}], \"name\": \"d8aca655-5bea-4016-b19e-3ca12781e43a\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 2, \"tags\": [\"normal\"]}], \"name\": \"8322a27a-88ed-4b74-af7c-995b4a4838f7\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 3, \"tags\": [\"normal\"]}], \"name\": \"18bd54b0-e9c7-4d09-9f0a-5791d6885491\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 4, \"tags\": [\"normal\"]}], \"name\": \"a970bbb9-2072-4f3b-9215-6333651a2abd\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 5, \"tags\": [\"normal\"]}], \"name\": \"5da9af72-7612-4e6e-ae68-f1f7fae2082c\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 6, \"tags\": [\"normal\"]}], \"name\": \"0e46623d-b9b9-485a-85bc-b8b47673ab3f\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 7, \"tags\": [\"normal\"]}], \"name\": \"219e013d-b918-4c67-8e94-e05ad673980e\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 8, \"tags\": [\"normal\"]}], \"name\": \"6be9def5-6319-465c-8865-f923420c6702\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 9, \"tags\": [\"normal\"]}], \"name\": \"ae65fd4c-f47d-4011-8249-5558a1f4d5c9\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 10, \"tags\": [\"normal\"]}], \"name\": \"849c4cf6-4cb5-49ac-8f98-71120dabab7c\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 11, \"tags\": [\"normal\"]}], \"name\": \"62fa5b32-7b19-4598-b1f3-6790d8e11f11\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 12, \"tags\": [\"normal\"]}], \"name\": \"80f2f443-0f6a-4438-b7bc-02e1a030b59d\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 13, \"tags\": [\"normal\"]}], \"name\": \"cbb0fc38-ca00-4f60-b4d3-104b767f68dd\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 14, \"tags\": [\"normal\"]}], \"name\": \"583e93fe-730e-42a7-8f6f-976d22ec2d9e\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 15, \"tags\": [\"normal\"]}], \"name\": \"b091da5d-f9fe-485f-ba38-60e0e75220af\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 16, \"tags\": [\"normal\"]}], \"name\": \"e5c2e87d-2084-421e-b57f-e8cc682a3ee5\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 17, \"tags\": [\"normal\"]}], \"name\": \"c58ebabf-8ef4-482a-9100-4aed56fe9056\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 18, \"tags\": [\"normal\"]}], \"name\": \"b7fe6bad-372f-47e1-b598-ea78cc81c053\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 19, \"tags\": [\"normal\"]}], \"name\": \"c8eb2873-04fe-4b48-a7bd-51e5f3a6e45b\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 20, \"tags\": [\"normal\"]}], \"name\": \"0deeaf5d-2698-4ff0-9e34-ed12301897f7\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 21, \"tags\": [\"normal\"]}], \"name\": \"5ecc04dd-94c5-4c53-b347-3155a4487459\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 22, \"tags\": [\"normal\"]}], \"name\": \"b13d9838-702c-4fc5-b5c0-25ff2531ef31\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 23, \"tags\": [\"normal\"]}], \"name\": \"6d93b17b-5d71-4e76-94c2-618f34a04242\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 24, \"tags\": [\"normal\"]}], \"name\": \"c3323791-0219-4e5c-9593-208ce44b9eee\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 25, \"tags\": [\"normal\"]}], \"name\": \"0f33288e-c299-431d-9eed-83c4e3370831\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 26, \"tags\": [\"normal\"]}], \"name\": \"f10ffb89-db66-4211-93ce-68c7762ec479\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 27, \"tags\": [\"normal\"]}], \"name\": \"7d16c9e0-fde7-49d7-9d8a-03ebddb30fb9\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 28, \"tags\": [\"normal\"]}], \"name\": \"5be1d076-4f2c-44b2-8539-fa44d298c4ef\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 29, \"tags\": [\"normal\"]}], \"name\": \"11dbfa01-e393-4295-9e09-2e11caed2611\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 30, \"tags\": [\"normal\"]}], \"name\": \"e044acc8-b34a-459e-aaef-199d442d4652\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 31, \"tags\": [\"normal\"]}], \"name\": \"725a17ac-9873-4cfc-9520-8033f63cf20f\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 32, \"tags\": [\"normal\"]}], \"name\": \"a2b87bf9-54e0-4875-b970-b4c6dc786bfa\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 33, \"tags\": [\"normal\"]}], \"name\": \"5f859954-2e88-40be-a58e-8b974a228e72\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 34, \"tags\": [\"normal\"]}], \"name\": \"0cb9a188-03ce-44db-bd54-0e8e8406ea6e\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 35, \"tags\": [\"normal\"]}], \"name\": \"05798da3-82b4-42b5-a0fb-76c2d51b7b7e\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 36, \"tags\": [\"normal\"]}], \"name\": \"77f62fb3-6610-4e0e-b51e-694c638ba8d7\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 37, \"tags\": [\"normal\"]}], \"name\": \"7bb85df8-ae5f-4877-8600-cb1b3c8a6212\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 38, \"tags\": [\"normal\"]}], \"name\": \"e9f8eea1-51f4-406b-adbc-5c3046f9645e\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 39, \"tags\": [\"normal\"]}], \"name\": \"08d91df1-c1a8-4b4c-9aba-cf0c1730547d\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 40, \"tags\": [\"normal\"]}], \"name\": \"b3fd77ee-2609-4796-b517-0202d5138c31\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 41, \"tags\": [\"normal\"]}], \"name\": \"1cf2aa0d-589e-4acf-add5-6ab9552cda9e\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 42, \"tags\": [\"normal\"]}], \"name\": \"03ebef3c-0154-4abe-8031-de75e0175b81\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 43, \"tags\": [\"normal\"]}], \"name\": \"3c3b8ca5-c0ae-46ec-8211-18de083364bd\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 44, \"tags\": [\"normal\"]}], \"name\": \"d318b66c-8b94-42e5-8ab6-69053296037a\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 45, \"tags\": [\"normal\"]}], \"name\": \"605b0a32-ee97-4264-ace6-23d12c4bce40\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 46, \"tags\": [\"normal\"]}], \"name\": \"08ff2bd6-6e46-4937-97b8-95c85d0ad301\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 47, \"tags\": [\"normal\"]}], \"name\": \"2f2c20f7-b772-43de-b6bc-bfa329c61c41\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 48, \"tags\": [\"normal\"]}], \"name\": \"fe4b53d9-571e-499b-a0e1-505ac7bc52ac\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 49, \"tags\": [\"normal\"]}], \"name\": \"1663c349-fc01-4a36-bf70-228d6a1d21ce\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 50, \"tags\": [\"normal\"]}], \"name\": \"e0249fb4-7a51-4a26-ae7f-e96996092beb\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 51, \"tags\": [\"normal\"]}], \"name\": \"043a66c7-fd42-4d87-8041-8fc86f706aa7\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 52, \"tags\": [\"normal\"]}], \"name\": \"b303a707-471a-41dc-ae29-06808fd958f7\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 53, \"tags\": [\"normal\"]}], \"name\": \"b914b9a6-cbf3-427e-a0be-c1602cccb597\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 54, \"tags\": [\"normal\"]}], \"name\": \"ce7e3637-fafd-4f69-bba9-08eb1a355001\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 55, \"tags\": [\"normal\"]}], \"name\": \"461bd4e8-fe53-464d-bb6a-89166971c5dd\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 56, \"tags\": [\"normal\"]}], \"name\": \"1891e165-d8dc-4276-bc14-a73cbc68b8fe\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 57, \"tags\": [\"normal\"]}], \"name\": \"525db04c-dcc2-46b5-b79f-3c02029769fb\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 58, \"tags\": [\"normal\"]}], \"name\": \"4eed4963-aa21-40ac-bf92-855e2635d672\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 59, \"tags\": [\"normal\"]}], \"name\": \"6c512285-17f9-4b41-8c16-06a0b8b0e7db\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 60, \"tags\": [\"normal\"]}], \"name\": \"0842052f-5e17-4038-8bd4-13eff0c66fd4\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 61, \"tags\": [\"normal\"]}], \"name\": \"835f540d-4311-41b6-84b8-3dbb2801ce0a\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 62, \"tags\": [\"normal\"]}], \"name\": \"31ac6805-61d1-4fcc-a573-a89b7b457dcc\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 63, \"tags\": [\"normal\"]}], \"name\": \"237df540-da64-4f33-8090-6a79e2548559\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 64, \"tags\": [\"normal\"]}], \"name\": \"1fb66889-42ee-48b1-b7c7-e271e5a72e2c\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 65, \"tags\": [\"normal\"]}], \"name\": \"ea6b688e-aed1-43f8-ab35-0ebc35939a85\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 66, \"tags\": [\"normal\"]}], \"name\": \"729dc29e-9594-4ecd-8102-b7b0f315a1e3\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 67, \"tags\": [\"normal\"]}], \"name\": \"68f78e68-c3f5-48c9-8bb1-7dc417ff0fbb\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 68, \"tags\": [\"normal\"]}], \"name\": \"db834d93-da57-4d81-872c-230422d65515\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 69, \"tags\": [\"normal\"]}], \"name\": \"217b4f51-f99c-485c-bc25-e381f94fdbe3\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 70, \"tags\": [\"normal\"]}], \"name\": \"3640b006-ed90-4166-a56b-fad075cdb65f\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 71, \"tags\": [\"normal\"]}], \"name\": \"3466ca69-d1b9-4872-b9b3-7c4f8b30cbfb\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 72, \"tags\": [\"normal\"]}], \"name\": \"7d02a03f-fedf-4673-87ea-1cf2c234c13a\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 73, \"tags\": [\"normal\"]}], \"name\": \"2d2de350-acee-4bbf-85c3-ae2709fd2c37\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 74, \"tags\": [\"normal\"]}], \"name\": \"c79f6872-048f-4098-ad60-5ad530b8eb0e\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 75, \"tags\": [\"normal\"]}], \"name\": \"aff18c11-66dd-42c2-b570-c95f582eaaac\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 76, \"tags\": [\"normal\"]}], \"name\": \"6fedaae3-eaa5-4baa-bb19-6e3f06f4d238\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 77, \"tags\": [\"normal\"]}], \"name\": \"4e904772-ce71-41f9-ba1a-a3c41fce18da\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 78, \"tags\": [\"normal\"]}], \"name\": \"f4c7c487-5263-4443-80e0-04a1feae0fa4\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 79, \"tags\": [\"normal\"]}], \"name\": \"187fa9b9-32a1-450b-ad5d-2bf5c08ad5e5\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 80, \"tags\": [\"normal\"]}], \"name\": \"baec7d0f-18ae-4661-8b87-7b98a9a3d466\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 81, \"tags\": [\"normal\"]}], \"name\": \"a7943a01-2925-42ef-9283-6b3a94e2a9d9\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 82, \"tags\": [\"normal\"]}], \"name\": \"6d7bb499-5366-4c05-a234-03b80f3c1b13\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 83, \"tags\": [\"normal\"]}], \"name\": \"52455223-12b4-4906-8baa-8b3a34549419\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 84, \"tags\": [\"normal\"]}], \"name\": \"f73a572c-3cd3-4ffb-b41e-1d812c96ad86\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 85, \"tags\": [\"normal\"]}], \"name\": \"1dfbc58a-8487-4f26-8a6e-e04b01f03bd8\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 86, \"tags\": [\"normal\"]}], \"name\": \"36cba822-c385-4988-b951-85901c808b30\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 87, \"tags\": [\"normal\"]}], \"name\": \"8ef2c52e-9cc9-47aa-aac7-e347d4d471d0\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 88, \"tags\": [\"normal\"]}], \"name\": \"ae03010e-0a5e-4fbb-98f2-57dcb1e1f306\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 89, \"tags\": [\"normal\"]}], \"name\": \"f072c0bc-ab25-4b86-a3df-4823fe6c7dab\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 90, \"tags\": [\"normal\"]}], \"name\": \"9901c1ca-c525-4041-a226-922f33fdf5fe\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 91, \"tags\": [\"normal\"]}], \"name\": \"00528e18-c921-48ef-8386-54770b464351\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 92, \"tags\": [\"normal\"]}], \"name\": \"dd2bd5e9-998a-4de7-94e4-f9499a70cf4a\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 93, \"tags\": [\"normal\"]}], \"name\": \"1f07ec6d-ddc8-4fd8-8c76-a4cfab301b2d\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 94, \"tags\": [\"normal\"]}], \"name\": \"541141f4-8dbf-47e2-a1c3-88de2d97a85c\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 95, \"tags\": [\"normal\"]}], \"name\": \"9cbe1e57-de8c-445d-ad63-60a79dfaed2b\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 96, \"tags\": [\"normal\"]}], \"name\": \"39d06f37-ab69-472b-83ea-42f1fe965b4f\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 97, \"tags\": [\"normal\"]}], \"name\": \"f15e6eaf-4702-4078-80f9-ae92b858d43d\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 98, \"tags\": [\"normal\"]}], \"name\": \"e52432d4-7b4d-4e26-ae40-fa76c016cb5f\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 99, \"tags\": [\"normal\"]}], \"name\": \"cef72cad-b124-4ff1-ae2a-f77047416c4d\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 100, \"tags\": [\"normal\"]}], \"name\": \"38649d2f-0da1-4c53-98be-9ba9af6513c7\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 101, \"tags\": [\"normal\"]}], \"name\": \"17c164ba-f369-444c-bddc-6c8e6e35fe3e\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 102, \"tags\": [\"normal\"]}], \"name\": \"0ccae693-044f-43c6-a2bc-22aa189eb3a6\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 103, \"tags\": [\"normal\"]}], \"name\": \"302db61f-eeea-4eac-90de-aeddfcd3342f\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 104, \"tags\": [\"normal\"]}], \"name\": \"07b8d6c4-63b5-4745-8f90-279514b01865\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 105, \"tags\": [\"normal\"]}], \"name\": \"325c457a-aa09-42a9-a5dd-111b7dab6b3b\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 106, \"tags\": [\"normal\"]}], \"name\": \"d3636c60-11e5-4747-b0b8-3212e64d598a\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 107, \"tags\": [\"normal\"]}], \"name\": \"4c4eeb03-c9e9-41d0-9d0f-68ab2bcc4d5e\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 108, \"tags\": [\"normal\"]}], \"name\": \"baec6ed4-5adb-4890-a4eb-fb7643338a1d\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 109, \"tags\": [\"normal\"]}], \"name\": \"0d1218b9-843d-453d-a632-32dc3c9aa39e\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 110, \"tags\": [\"normal\"]}], \"name\": \"99c12076-c260-4675-84e9-fa9deaa95520\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 111, \"tags\": [\"normal\"]}], \"name\": \"560d177b-7cc6-415f-b1fc-e62d28d81c36\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 112, \"tags\": [\"normal\"]}], \"name\": \"0e4464c8-465b-45ae-81ed-a241b66006a0\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 113, \"tags\": [\"normal\"]}], \"name\": \"7c5f616e-7478-4e97-a468-ff5be83edddd\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 114, \"tags\": [\"normal\"]}], \"name\": \"4c75295f-f67d-44e6-abf0-a52016d1211f\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 115, \"tags\": [\"normal\"]}], \"name\": \"ad049fe6-7323-4871-9b80-1a9e73c8a64f\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 116, \"tags\": [\"normal\"]}], \"name\": \"dcba7d43-42aa-49d5-b1c3-4c8809231ba6\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 117, \"tags\": [\"normal\"]}], \"name\": \"896f3c34-8c5d-45ed-be8f-98ba504f24ea\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 118, \"tags\": [\"normal\"]}], \"name\": \"fa6eb4de-06a1-4d4f-a7d9-2f771dbdf7e3\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 119, \"tags\": [\"normal\"]}], \"name\": \"f32c9745-b008-4025-8d62-66c73d5075f8\", \"auto_diff_type\": 1, \"max_iterations\": 20}, {\"enabled\": true, \"frame_list\": [{\"number\": 120, \"tags\": [\"normal\"]}], \"name\": \"475ea273-bc76-4d31-a732-e89ef3ea1621\", \"auto_diff_type\": 1, \"max_iterations\": 20}]");
	setAttr -l on ".solver_step_list" -type "string" "[{\"name\": \"7b5c83ec-7682-4ed6-a5d2-b4ef051529f9\", \"frame_list\": [1, 30, 60, 90, 120], \"use_static_attrs\": true, \"enabled\": true, \"use_anim_attrs\": true, \"strategy\": \"all_frames_at_once\"}, {\"name\": \"e3c4e160-b86b-4230-96a4-d5f0e18044a0\", \"frame_list\": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120], \"use_static_attrs\": false, \"enabled\": true, \"use_anim_attrs\": true, \"strategy\": \"two_frames_fwd\"}]";
	setAttr -l on ".override_current_frame";
	setAttr -l on ".object_toggle_camera";
	setAttr -l on ".object_toggle_marker";
	setAttr -l on ".object_toggle_bundle";
createNode animCurveTL -n "camera1_translateX";
	rename -uid "92745BFF-47AC-3289-78EE-9DAA232D3C31";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 21.986628916650904 2 21.986780330009939
		 3 21.987177229605322 4 21.98782357830888 5 21.988729728341781 6 21.989877207055859
		 7 21.991274132861957 8 21.992892186670119 9 21.994756380838471 10 21.996850950383699
		 11 21.999193430156353 12 22.001708897311698 13 22.004464849058518 14 22.007432587856385
		 15 22.010607655525362 16 22.01398558762321 17 22.017561927971599 18 22.021332211404236
		 19 22.02529198129027 20 22.029436772756615 21 22.033762125788428 22 22.038263580237803
		 23 22.042936673823512 24 22.047776945343323 25 22.052779934125159 26 22.057941178425999
		 27 22.0632562167198 28 22.068720587879405 29 22.074329829836277 30 22.080079482982395
		 31 22.085965085993731 32 22.091982174946551 33 22.098126289806459 34 22.104392969796628
		 35 22.110777753190984 36 22.117276177449831 37 22.123883781083922 38 22.130596103677828
		 39 22.137408681910905 40 22.144317055871859 41 22.151316761561439 42 22.158403339894136
		 43 22.165572330176879 44 22.172819269812251 45 22.180139702178501 46 22.187529167893793
		 47 22.194983213830984 48 22.202497383650062 49 22.2100672304739 50 22.217688304789689
		 51 22.225356164436352 52 22.233066370663266 53 22.240814496630296 54 22.248596115151649
		 55 22.256406807753525 56 22.264242167191945 57 22.272097791067548 58 22.279969288801141
		 59 22.287852277254146 60 22.295742382087969 61 22.303635242586122 62 22.311526496763395
		 63 22.319411804127125 64 22.327286818816937 65 22.335147210558663 66 22.342988637313873
		 67 22.350806780601772 68 22.358597303792294 69 22.366355881713986 70 22.374078171389112
		 71 22.381759834090566 72 22.389396519657378 73 22.396983852484944 74 22.404517425060238
		 75 22.411992900730116 76 22.419405868069937 77 22.426751907487873 78 22.434026469673373
		 79 22.441225118904466 80 22.448343339841472 81 22.455376678016119 82 22.462320555412006
		 83 22.469170392985873 84 22.475921607616257 85 22.482569663150159 86 22.48910979137435
		 87 22.495537456618131 88 22.501848043630648 89 22.508036772538958 90 22.514099075712519
		 91 22.520030286533355 92 22.525825717348674 93 22.531480695782438 94 22.536990564008907
		 95 22.54235067757168 96 22.547556337923552 97 22.552602966279228 98 22.557485900255127
		 99 22.562200500442604 100 22.566742208558715 101 22.571106409653286 102 22.575288561238054
		 103 22.57928404896241 104 22.58308829099558 105 22.586696878006663 106 22.59010517198185
		 107 22.593308727360188 108 22.596302985729885 109 22.599083493019581 110 22.601645776404485
		 111 22.603985307735254 112 22.606097648163445 113 22.607978340745071 114 22.609622890268287
		 115 22.611026798075489 116 22.612185676090704 117 22.613095018091677 118 22.613752383496251
		 119 22.61414852636026 120 22.614281036820206;
	setAttr -s 120 ".kit[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 18;
	setAttr -s 120 ".kot[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 18;
createNode animCurveTL -n "camera1_translateY";
	rename -uid "D95A4D03-4A5A-5B4A-0B06-1FB2096810CD";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 27.788688015994975 2 27.785428195348103
		 3 27.775804521680428 4 27.759870214700733 5 27.737759739759127 6 27.709579064314116
		 7 27.675428635256083 8 27.635440588551628 9 27.589699116981674 10 27.538321304587079
		 11 27.481409800159899 12 27.419105377169135 13 27.351482378528857 14 27.278662514262532
		 15 27.200755194186247 16 27.117869818749682 17 27.030115799644211 18 26.937602542135814
		 19 26.840439450718538 20 26.738735935304717 21 26.632601398759903 22 26.522145249500696
		 23 26.40747689448893 24 26.288705740527803 25 26.165941193583848 26 26.039292661756299
		 27 25.908869549540391 28 25.774781267787464 29 25.637137221118394 30 25.496046815907476
		 31 25.35161946391154 32 25.203964569120746 33 25.053191539846605 34 24.899409783048437
		 35 24.742728708492105 36 24.583257722753771 37 24.42110623487579 38 24.256383649458542
		 39 24.089199376793239 40 23.919662823787871 41 23.747883398809247 42 23.573970510623781
		 43 23.39803356698819 44 23.220181977386279 45 23.040525152573657 46 22.859172501548755
		 47 22.676233440679994 48 22.491817380127166 49 22.306033737475708 50 22.118991929417803
		 51 21.930801376669724 52 21.74157149943888 53 21.551411728512186 54 21.360431486885417
		 55 21.168740206077061 56 20.976447319215872 57 20.783662262475115 58 20.590494472336385
		 59 20.397053385826545 60 20.203448445364295 61 20.009789089998335 62 19.816184755436453
		 63 19.622744881494036 64 19.429578901900488 65 19.236796249452791 66 19.044506344258281
		 67 18.852818613744031 68 18.661842465257266 69 18.471687311026386 70 18.282462546061158
		 71 18.094277562644585 72 17.907241746175742 73 17.721464466750099 74 17.537055108121859
		 75 17.35412299355318 76 17.172777616750711 77 16.993127943612137 78 16.815283705313657
		 79 16.639354107180328 80 16.465448495966626 81 16.293676175282879 82 16.124146506639114
		 83 15.956968814250926 84 15.79225244070952 85 15.630106731345444 86 15.470641055381313
		 87 15.31396476122443 88 15.160187233482416 89 15.009417826751671 90 14.861765938470951
		 91 14.717340962716007 92 14.576252314022074 93 14.438609402172911 94 14.304521666901413
		 95 14.174098526100117 96 14.047449427393612 97 13.924683827926586 98 13.805911192487979
		 99 13.691240943057402 100 13.580782596079338 101 13.474645596157886 102 13.372939421983705
		 103 13.275773550450996 104 13.183257457589637 105 13.095500607627594 106 13.012612480318285
		 107 12.934702559646119 108 12.861880291276741 109 12.794255170768155 110 12.731936635083104
		 111 12.675034134342832 112 12.62365715777181 113 12.577915123111532 114 12.537917496888998
		 115 12.503773705753424 116 12.47559319119085 117 12.453485357633355 118 12.437558878733656
		 119 12.427927840172352 120 12.424692275551864;
	setAttr -s 120 ".kit[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 18;
	setAttr -s 120 ".kot[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 18;
createNode animCurveTL -n "camera1_translateZ";
	rename -uid "F0E83150-4A15-5213-98C1-63BAB285B746";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 39.335079233335279 2 39.332303932513923
		 3 39.324110147702633 4 39.310567609618055 5 39.291766022402257 6 39.267805513929517
		 7 39.238770201460859 8 39.204770791171903 9 39.165878769873451 10 39.122194265533579
		 11 39.073797348918298 12 39.020830243636247 13 38.963333333549173 14 38.901417766814468
		 15 38.83517657102712 16 38.764702771307945 17 38.690089394742337 18 38.611429468658194
		 19 38.528816018127706 20 38.442342072327158 21 38.35210065616441 22 38.258184796993788
		 23 38.160687522143135 24 38.059701859240789 25 37.955320834526425 26 37.847637474910002
		 27 37.736744807441646 28 37.622735859912055 29 37.505703658350484 30 37.385741229416652
		 31 37.26294160061348 32 37.137397798731286 33 37.009202849812489 34 36.878449779910554
		 35 36.745231616088361 36 36.609641383840007 37 36.471772110271075 38 36.331716818900752
		 39 36.189568536656587 40 36.045420287327097 41 35.899365097432955 42 35.751495990440837
		 43 35.601905990404205 44 35.450688123170949 45 35.297935411180703 46 35.143740878540967
		 47 34.988197548604511 48 34.831398444652891 49 34.673436589061815 50 34.514405004421626
		 51 34.354396713422418 52 34.193504736254454 53 34.031822094694462 54 33.869441808189954
		 55 33.706456895403051 56 33.542960373103554 57 33.379045258410457 58 33.214804565194875
		 59 33.050331305041915 60 32.885718489693602 61 32.721059126052261 62 32.55644622080635
		 63 32.391972774678109 64 32.227731787895671 65 32.063816261247197 66 31.900319184530701
		 67 31.737333552256338 68 31.574952353798796 69 31.413268575390514 70 31.252375202540055
		 71 31.092365221729455 72 30.933331611160302 73 30.775367353942212 74 30.618565402374088
		 75 30.463018825059436 76 30.308820512650499 77 30.156063539922734 78 30.004840819100991
		 79 29.85524537726489 80 29.707370192173794 81 29.561308292373266 82 29.417152679774446
		 83 29.274996360839786 84 29.134932366570268 85 28.997053716534381 86 28.861453444615208
		 87 28.728224589106169 88 28.59746019083671 89 28.469253327574002 90 28.343697052367617
		 91 28.220884425559518 92 28.100908520894524 93 27.983862421836093 94 27.86983921692379
		 95 27.758931982268034 96 27.651233827896466 97 27.546837821006648 98 27.445837093702757
		 99 27.348324705112752 100 27.254393779524182 101 27.164137401178937 102 27.077648682813198
		 103 26.995020709983795 104 26.916346599671108 105 26.841719413981 106 26.771232270082251
		 107 26.70497822951355 108 26.643050415215374 109 26.585541877650098 110 26.532545709340958
		 111 26.484154997262284 112 26.44046279800742 113 26.401562182176498 114 26.367546228056323
		 115 26.338507998171554 116 26.314540540536736 117 26.295736937160157 118 26.282188457410669
		 119 26.27399195305939 120 26.271239700911067;
	setAttr -s 120 ".kit[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 18;
	setAttr -s 120 ".kot[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 18;
createNode animCurveTA -n "camera1_rotateX";
	rename -uid "022FF2BC-4B6E-B225-AF88-60976426DE7D";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 -31.533393056540497 2 -31.531231358175148
		 3 -31.52480297566494 4 -31.514149804227117 5 -31.499377128431458 6 -31.480545189932204
		 7 -31.457725201148325 8 -31.431000422951819 9 -31.400434360683157 10 -31.366102816834324
		 11 -31.328082084043999 12 -31.286437566730459 13 -31.241249457811438 14 -31.192588603704245
		 15 -31.140528112861954 16 -31.08514108589161 17 -31.02650063487097 18 -30.964679862634096
		 19 -30.899751874213685 20 -30.83178977704144 21 -30.760866673076343 22 -30.687055670291723
		 23 -30.610429872740465 24 -30.531062385550374 25 -30.4490263127934 26 -30.364394760774196
		 27 -30.277240831832497 28 -30.18763763362761 29 -30.095658269245664 30 -30.001375842768585
		 31 -29.904863462947528 32 -29.806194229858214 33 -29.705441250947093 34 -29.602677630187067
		 35 -29.497976474075692 36 -29.391410886966945 37 -29.283053974576351 38 -29.172978840698303
		 39 -29.061258591996413 40 -28.947966334986692 41 -28.833175174472768 42 -28.716958218988889
		 43 -28.599388574969115 44 -28.480539350165262 45 -28.360483656249198 46 -28.239294602135068
		 47 -28.117045305276402 48 -27.993808877121293 49 -27.869658440299396 50 -27.74466711367721
		 51 -27.618908023549871 52 -27.49245429774124 53 -27.365379077158913 54 -27.23775549624002
		 55 -27.10965670034663 56 -26.981155840640454 57 -26.852326072532996 58 -26.723240557394611
		 59 -26.59397246047693 60 -26.464594952902036 61 -26.335181211527598 62 -26.205804407770206
		 63 -26.076537727445547 64 -25.947454347699274 65 -25.818627448948678 66 -25.690130202655734
		 67 -25.56203578701615 68 -25.434417364541886 69 -25.307348099280414 70 -25.180901136997516
		 71 -25.055149617899747 72 -24.930166677696963 73 -24.806025424546096 74 -24.682798998180125
		 75 -24.560560389180235 76 -24.439382994334654 77 -24.319339160057176 78 -24.200502619162066
		 79 -24.082946174435335 80 -23.96674287167172 81 -23.851965703314541 82 -23.738687692038134
		 83 -23.626981830194964 84 -23.516921113115895 85 -23.40857856501361 86 -23.302027147341548
		 87 -23.197339886724102 88 -23.094589810848859 89 -22.993849862287526 90 -22.895193113650116
		 91 -22.798692591407033 92 -22.70442134023164 93 -22.612452403243971 94 -22.522858848573797
		 95 -22.435713764237171 96 -22.35109022299137 97 -22.269061368963957 98 -22.189700295907922
		 99 -22.113080106972429 100 -22.039273998392815 101 -21.968355103521514 102 -21.900396565038285
		 103 -21.835471578138883 104 -21.773653291997341 105 -21.71501489499019 106 -21.65962957605527
		 107 -21.60757053768884 108 -21.55891091480116 109 -21.513723962112476 110 -21.472082804852988
		 111 -21.434060624396729 112 -21.399730637879298 113 -21.369165979632292 114 -21.342439842723426
		 115 -21.31962537196166 116 -21.300795714626538 117 -21.286023974738178 118 -21.275387029636189
		 119 -21.268953230884179 120 -21.266787789093463;
	setAttr -s 120 ".kit[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 18;
	setAttr -s 120 ".kot[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 18;
createNode animCurveTA -n "camera1_rotateY";
	rename -uid "02AAFDA8-4D29-A71D-490B-8793BF7F4266";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 33.59999346375271 2 33.601193385034961
		 3 33.604712425911224 4 33.610519124752102 5 33.618583157376015 6 33.628853451611491
		 7 33.641306122898136 8 33.655869334221123 9 33.672541531938485 10 33.691268327676674
		 11 33.712035983417252 12 33.734720782607894 13 33.759368489936392 14 33.785910374590408
		 15 33.814306559089822 16 33.844517160722845 17 33.876502302222185 18 33.910222100427909
		 19 33.945636679571244 20 33.982706154297489 21 34.021390647135782 22 34.061650276702913
		 23 34.103445162604586 24 34.146735423054253 25 34.191481178940293 26 34.237642548801411
		 27 34.285179651380261 28 34.33405260631617 29 34.384221531736699 30 34.435646548595145
		 31 34.488287775834934 32 34.542105331157799 33 34.597059333430451 34 34.653109903234785
		 35 34.710217159108858 36 34.76834121904065 37 34.82744220136 38 34.887480226851068
		 39 34.948415412023991 40 35.010207877225696 41 35.072817738541772 42 35.136205117027821
		 43 35.20033013279577 44 35.265152901534734 45 35.330633547740767 46 35.396732191145865
		 47 35.463408959467671 48 35.530623976038676 49 35.59833737309522 50 35.666509283472195
		 51 35.735099845139366 52 35.804069202538734 53 35.873377510885817 54 35.942984926994789
		 55 36.012851619554937 56 36.082937770160328 57 36.153203566712101 58 36.223609212448608
		 59 36.294114921577538 60 36.364680921733409 61 36.435267457138742 62 36.505834775694375
		 63 36.576343153288846 64 36.646752866238515 65 36.71702420664262 66 36.787117468371797
		 67 36.856992970976549 68 36.926611016080187 69 36.995931931630238 70 37.064916025733524
		 71 37.133523614851605 72 37.201715014021559 73 37.269450509664871 74 37.336690398328209
		 75 37.403394907574587 76 37.469524347520071 77 37.535038949057558 78 37.599898845098146
		 79 37.664064227991709 80 37.727495258362111 81 37.79015205463196 82 37.851994691579463
		 83 37.912983205506897 84 37.973077600163329 85 38.032237925886442 86 38.090424013185491
		 87 38.147595872240622 88 38.203713451976839 89 38.258736467032094 90 38.312624864656193
		 91 38.365338497228429 92 38.416837167424745 93 38.467080670883632 94 38.516028821986005
		 95 38.563641432065801 96 38.609878225337944 97 38.654699104640123 98 38.698063800353104
		 99 38.739932134901537 100 38.780263964791402 101 38.819019104188314 102 38.856157438383761
		 103 38.891638772305328 104 38.925422926429292 105 38.957469995263885 106 38.987739708299245
		 107 39.016192126511591 108 39.042787072430919 109 39.067484597275545 110 39.0902446820187
		 111 39.111027228097221 112 39.129792316957229 113 39.146499968738638 114 39.161110154923747
		 115 39.173582861812307 116 39.183878254706897 117 39.191956285734285 118 39.197779825272661
		 119 39.201302819232332 120 39.202486707187965;
	setAttr -s 120 ".kit[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 18;
	setAttr -s 120 ".kot[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 18;
createNode animCurveTA -n "camera1_rotateZ";
	rename -uid "F342F783-4465-B339-D6A7-A58EAF2C4B01";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 120 ".ktv[0:119]"  1 359.99998967191078 2 359.99995473801471
		 3 359.99995850062288 4 359.99996467702755 5 359.9999593730555 6 359.99996071744619
		 7 359.99995614207808 8 359.99996725533543 9 359.99996731337848 10 359.99996565420258
		 11 359.99994376869881 12 359.999967577961 13 359.99996770145458 14 359.99996784807587
		 15 359.99996802023526 16 359.99996822363096 17 359.99996845595155 18 359.99996872615094
		 19 359.99996903403468 20 359.9999693859445 21 359.99996978689518 22 359.99997023779048
		 23 359.99997074634257 24 359.99997131612611 25 359.99997195263984 26 359.99997266087246
		 27 359.99997344596096 28 359.99997431461054 29 359.99997527183359 30 359.99997632218674
		 31 359.99997747226507 32 359.99997873218865 33 359.999980104266 34 359.99998159569827
		 35 359.99998321395128 36 359.99998496616445 37 359.99998685945695 38 359.99998889864571
		 39 359.99999109290616 40 359.99999344576878 41 359.99999596706687 42 359.99999866012087
		 43 360.00000153075194 44 360.00000458505559 45 360.00000782462183 46 360.00001125218665
		 47 360.00001486775972 48 360.00001867131596 49 360.00002265297593 50 360.00002681043617
		 51 360.00003113168265 52 360.00003560214759 53 360.00004019754454 54 360.00004489192992
		 55 360.00004965530053 56 360.00005444565232 57 360.0000592186102 58 360.00006391686128
		 59 360.00006847643266 60 360.00007283121465 61 360.0000768949746 62 360.00008058694146
		 63 360.00008380356945 64 360.00008644968449 65 360.00008841212963 66 360.00008958614251
		 67 360.00008985238202 68 360.00008909055975 69 360.00008718629385 70 360.0000840295225
		 71 360.00007950895491 72 360.00007352163141 73 360.00006598645967 74 360.00005680680647
		 75 360.00004596564497 76 360.00003322727054 77 360.00001888080203 78 360.00000266897359
		 79 359.99998468268262 80 359.99996493121176 81 359.99994343265257 82 359.99992028253729
		 83 359.99989556689371 84 359.99986938689659 85 359.99984180929169 86 359.99981311027932
		 87 359.99978333539025 88 359.99975263692119 89 359.99972128146339 90 359.99968938447574
		 91 359.99965710684006 92 359.99962466192602 93 359.99959223316063 94 359.99956002649793
		 95 359.999528161716 96 359.99949686844633 97 359.99946624398285 98 359.99943648963267
		 99 359.99940772737335 100 359.99938007224392 101 359.99935362517164 102 359.99932849198996
		 103 359.99930476557086 104 359.99928256363228 105 359.9992618423471 106 359.99924271075241
		 107 359.9992251859768 108 359.99920931715548 109 359.99919509138812 110 359.99918251711534
		 111 359.99917159770132 112 359.99916235003872 113 359.99915472893991 114 359.99914874901447
		 115 359.99914440662394 116 359.99914167169516 117 359.9991405327728 118 359.99913323027255
		 119 359.99913859452198 120 359.99914668405188;
	setAttr -s 120 ".kit[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 18;
	setAttr -s 120 ".kot[0:119]"  18 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 
		2 2 2 2 2 2 2 2 2 18;
select -ne :time1;
	setAttr ".o" 83;
	setAttr ".unw" 83;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".aoon" yes;
	setAttr ".msaa" yes;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -s 10 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 12 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderUtilityList1;
	setAttr -s 4 ".u";
select -ne :defaultRenderingList1;
select -ne :defaultTextureList1;
	setAttr -s 4 ".tx";
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultResolution;
	setAttr ".w" 1920;
	setAttr ".h" 1080;
	setAttr ".pa" 1;
	setAttr ".dar" 1.7777777910232544;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
connectAttr "camera1_translateX.o" "camera1.tx";
connectAttr "camera1_translateY.o" "camera1.ty";
connectAttr "camera1_translateZ.o" "camera1.tz";
connectAttr "camera1_rotateX.o" "camera1.rx";
connectAttr "camera1_rotateY.o" "camera1.ry";
connectAttr "camera1_rotateZ.o" "camera1.rz";
connectAttr "imagePlaneShape1.msg" "cameraShape1.ip" -na;
connectAttr ":defaultColorMgtGlobals.cme" "imagePlaneShape1.cme";
connectAttr ":defaultColorMgtGlobals.cfe" "imagePlaneShape1.cmcf";
connectAttr ":defaultColorMgtGlobals.cfp" "imagePlaneShape1.cmcp";
connectAttr ":defaultColorMgtGlobals.wsn" "imagePlaneShape1.ws";
connectAttr "expression1.out[0]" "imagePlaneShape1.fe";
connectAttr "mmMarkerScale1.ot" "markerGroup1.t";
connectAttr "mmMarkerScale1.os" "markerGroup1.s";
connectAttr "pCube1_locator9_MKR_translateX.o" "pCube1_locator9_MKR.tx" -l on;
connectAttr "pCube1_locator9_MKR_translateY.o" "pCube1_locator9_MKR.ty" -l on;
connectAttr "pCube1_locator9_MKR_enable.o" "pCube1_locator9_MKR.enable" -l on;
connectAttr "pCube1_locator9_MKR_weight.o" "pCube1_locator9_MKR.weight";
connectAttr "pCube1_locator9_MKR.enable" "pCube1_locator9_MKR.lodv";
connectAttr "bundle1_BND.msg" "pCube1_locator9_MKR.bundle";
connectAttr "pCube1_locator10_MKR_translateX.o" "pCube1_locator10_MKR.tx" -l on;
connectAttr "pCube1_locator10_MKR_translateY.o" "pCube1_locator10_MKR.ty" -l on;
connectAttr "pCube1_locator10_MKR_enable.o" "pCube1_locator10_MKR.enable" -l on;
connectAttr "pCube1_locator10_MKR_weight.o" "pCube1_locator10_MKR.weight";
connectAttr "pCube1_locator10_MKR.enable" "pCube1_locator10_MKR.lodv";
connectAttr "bundle2_BND.msg" "pCube1_locator10_MKR.bundle";
connectAttr "pCube1_locator11_MKR_translateX.o" "pCube1_locator11_MKR.tx" -l on;
connectAttr "pCube1_locator11_MKR_translateY.o" "pCube1_locator11_MKR.ty" -l on;
connectAttr "pCube1_locator11_MKR_enable.o" "pCube1_locator11_MKR.enable" -l on;
connectAttr "pCube1_locator11_MKR_weight.o" "pCube1_locator11_MKR.weight";
connectAttr "pCube1_locator11_MKR.enable" "pCube1_locator11_MKR.lodv";
connectAttr "bundle3_BND.msg" "pCube1_locator11_MKR.bundle";
connectAttr "pCube1_locator12_MKR_translateX.o" "pCube1_locator12_MKR.tx" -l on;
connectAttr "pCube1_locator12_MKR_translateY.o" "pCube1_locator12_MKR.ty" -l on;
connectAttr "pCube1_locator12_MKR_enable.o" "pCube1_locator12_MKR.enable" -l on;
connectAttr "pCube1_locator12_MKR_weight.o" "pCube1_locator12_MKR.weight";
connectAttr "pCube1_locator12_MKR.enable" "pCube1_locator12_MKR.lodv";
connectAttr "bundle4_BND.msg" "pCube1_locator12_MKR.bundle";
connectAttr "locator1_MKR_translateX.o" "locator1_MKR.tx" -l on;
connectAttr "locator1_MKR_translateY.o" "locator1_MKR.ty" -l on;
connectAttr "locator1_MKR_enable.o" "locator1_MKR.enable" -l on;
connectAttr "locator1_MKR_weight.o" "locator1_MKR.weight";
connectAttr "locator1_MKR.enable" "locator1_MKR.lodv";
connectAttr "bundle5_BND.msg" "locator1_MKR.bundle";
connectAttr "locator2_MKR_translateX.o" "locator2_MKR.tx" -l on;
connectAttr "locator2_MKR_translateY.o" "locator2_MKR.ty" -l on;
connectAttr "locator2_MKR_enable.o" "locator2_MKR.enable" -l on;
connectAttr "locator2_MKR_weight.o" "locator2_MKR.weight";
connectAttr "locator2_MKR.enable" "locator2_MKR.lodv";
connectAttr "bundle6_BND.msg" "locator2_MKR.bundle";
connectAttr "locator3_MKR_translateX.o" "locator3_MKR.tx" -l on;
connectAttr "locator3_MKR_translateY.o" "locator3_MKR.ty" -l on;
connectAttr "locator3_MKR_enable.o" "locator3_MKR.enable" -l on;
connectAttr "locator3_MKR_weight.o" "locator3_MKR.weight";
connectAttr "locator3_MKR.enable" "locator3_MKR.lodv";
connectAttr "bundle7_BND.msg" "locator3_MKR.bundle";
connectAttr "locator4_MKR_translateX.o" "locator4_MKR.tx" -l on;
connectAttr "locator4_MKR_translateY.o" "locator4_MKR.ty" -l on;
connectAttr "locator4_MKR_enable.o" "locator4_MKR.enable" -l on;
connectAttr "locator4_MKR_weight.o" "locator4_MKR.weight";
connectAttr "locator4_MKR.enable" "locator4_MKR.lodv";
connectAttr "bundle8_BND.msg" "locator4_MKR.bundle";
connectAttr "locator5_MKR_translateX.o" "locator5_MKR.tx" -l on;
connectAttr "locator5_MKR_translateY.o" "locator5_MKR.ty" -l on;
connectAttr "locator5_MKR_enable.o" "locator5_MKR.enable" -l on;
connectAttr "locator5_MKR_weight.o" "locator5_MKR.weight";
connectAttr "locator5_MKR.enable" "locator5_MKR.lodv";
connectAttr "bundle9_BND.msg" "locator5_MKR.bundle";
connectAttr "locator6_MKR_translateX.o" "locator6_MKR.tx" -l on;
connectAttr "locator6_MKR_translateY.o" "locator6_MKR.ty" -l on;
connectAttr "locator6_MKR_enable.o" "locator6_MKR.enable" -l on;
connectAttr "locator6_MKR_weight.o" "locator6_MKR.weight";
connectAttr "locator6_MKR.enable" "locator6_MKR.lodv";
connectAttr "bundle10_BND.msg" "locator6_MKR.bundle";
connectAttr "locator7_MKR_translateX.o" "locator7_MKR.tx" -l on;
connectAttr "locator7_MKR_translateY.o" "locator7_MKR.ty" -l on;
connectAttr "locator7_MKR_enable.o" "locator7_MKR.enable" -l on;
connectAttr "locator7_MKR_weight.o" "locator7_MKR.weight";
connectAttr "locator7_MKR.enable" "locator7_MKR.lodv";
connectAttr "bundle11_BND.msg" "locator7_MKR.bundle";
connectAttr "locator8_MKR_translateX.o" "locator8_MKR.tx" -l on;
connectAttr "locator8_MKR_translateY.o" "locator8_MKR.ty" -l on;
connectAttr "locator8_MKR_enable.o" "locator8_MKR.enable" -l on;
connectAttr "locator8_MKR_weight.o" "locator8_MKR.weight";
connectAttr "locator8_MKR.enable" "locator8_MKR.lodv";
connectAttr "bundle12_BND.msg" "locator8_MKR.bundle";
connectAttr "geom:groupId2.id" "geom:pPlane1Shape.iog.og[0].gid";
connectAttr "geom:lambert2SG.mwc" "geom:pPlane1Shape.iog.og[0].gco";
connectAttr "geom:groupId4.id" "geom:pSphere1Shape.iog.og[0].gid";
connectAttr "geom:lambert4SG.mwc" "geom:pSphere1Shape.iog.og[0].gco";
connectAttr "geom:groupId1.id" "geom:pCone1Shape.iog.og[0].gid";
connectAttr "geom:lambert2SG.mwc" "geom:pCone1Shape.iog.og[0].gco";
connectAttr "geom:groupId5.id" "geom:pTorus1Shape.iog.og[0].gid";
connectAttr "geom:lambert5SG.mwc" "geom:pTorus1Shape.iog.og[0].gco";
connectAttr "geom:groupId3.id" "geom:pCylinder1Shape.iog.og[0].gid";
connectAttr "geom:lambert4SG.mwc" "geom:pCylinder1Shape.iog.og[0].gco";
connectAttr "pCube1_rotateZ.o" "geom:pCube1.rz";
connectAttr "pCube1_rotateY.o" "geom:pCube1.ry";
connectAttr "pCube1_rotateX.o" "geom:pCube1.rx";
connectAttr "pCube1_translateZ.o" "geom:pCube1.tz";
connectAttr "pCube1_translateY.o" "geom:pCube1.ty";
connectAttr "pCube1_translateX.o" "geom:pCube1.tx";
connectAttr "geom:groupId6.id" "geom:pCube1Shape.iog.og[0].gid";
connectAttr "geom:lambert3SG.mwc" "geom:pCube1Shape.iog.og[0].gco";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "lambert2SG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "lambert3SG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "lambert4SG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "lambert5SG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "geom:lambert2SG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "geom:lambert4SG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "geom:lambert5SG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "geom:lambert3SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "lambert2SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "lambert3SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "lambert4SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "lambert5SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "geom:lambert2SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "geom:lambert4SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "geom:lambert5SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "geom:lambert3SG.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "checker1.oc" "lambert2.c";
connectAttr "lambert2.oc" "lambert2SG.ss";
connectAttr "lambert2SG.msg" "materialInfo1.sg";
connectAttr "lambert2.msg" "materialInfo1.m";
connectAttr "checker1.msg" "materialInfo1.t" -na;
connectAttr "place2dTexture1.o" "checker1.uv";
connectAttr "place2dTexture1.ofs" "checker1.fs";
connectAttr "checker2.oc" "lambert3.c";
connectAttr "lambert3.oc" "lambert3SG.ss";
connectAttr "lambert3SG.msg" "materialInfo2.sg";
connectAttr "lambert3.msg" "materialInfo2.m";
connectAttr "checker2.msg" "materialInfo2.t" -na;
connectAttr "place2dTexture2.o" "checker2.uv";
connectAttr "place2dTexture2.ofs" "checker2.fs";
connectAttr "checker3.oc" "lambert4.c";
connectAttr "lambert4.oc" "lambert4SG.ss";
connectAttr "lambert4SG.msg" "materialInfo3.sg";
connectAttr "lambert4.msg" "materialInfo3.m";
connectAttr "checker3.msg" "materialInfo3.t" -na;
connectAttr "place2dTexture3.o" "checker3.uv";
connectAttr "place2dTexture3.ofs" "checker3.fs";
connectAttr "checker4.oc" "lambert5.c";
connectAttr "lambert5.oc" "lambert5SG.ss";
connectAttr "lambert5SG.msg" "materialInfo4.sg";
connectAttr "lambert5.msg" "materialInfo4.m";
connectAttr "checker4.msg" "materialInfo4.t" -na;
connectAttr "place2dTexture4.o" "checker4.uv";
connectAttr "place2dTexture4.ofs" "checker4.fs";
connectAttr "markerGroup1.depth" "mmMarkerScale1.dpt";
connectAttr "markerGroup1.overscan" "mmMarkerScale1.ovrscn";
connectAttr "cameraShape1.fl" "mmMarkerScale1.fl";
connectAttr "cameraShape1.cap" "mmMarkerScale1.cap";
connectAttr "cameraShape1.fio" "mmMarkerScale1.fio";
connectAttr ":time1.o" "expression1.tim";
connectAttr "geom:lambert2SG1.oc" "geom:lambert2SG.ss";
connectAttr "geom:groupId1.msg" "geom:lambert2SG.gn" -na;
connectAttr "geom:groupId2.msg" "geom:lambert2SG.gn" -na;
connectAttr "geom:pCone1Shape.iog.og[0]" "geom:lambert2SG.dsm" -na;
connectAttr "geom:pPlane1Shape.iog.og[0]" "geom:lambert2SG.dsm" -na;
connectAttr "geom:lambert2SG.msg" "geom:materialInfo1.sg";
connectAttr "geom:lambert2SG1.msg" "geom:materialInfo1.m";
connectAttr "geom:lambert4SG1.oc" "geom:lambert4SG.ss";
connectAttr "geom:groupId3.msg" "geom:lambert4SG.gn" -na;
connectAttr "geom:groupId4.msg" "geom:lambert4SG.gn" -na;
connectAttr "geom:pCylinder1Shape.iog.og[0]" "geom:lambert4SG.dsm" -na;
connectAttr "geom:pSphere1Shape.iog.og[0]" "geom:lambert4SG.dsm" -na;
connectAttr "geom:lambert4SG.msg" "geom:materialInfo2.sg";
connectAttr "geom:lambert4SG1.msg" "geom:materialInfo2.m";
connectAttr "geom:lambert5SG1.oc" "geom:lambert5SG.ss";
connectAttr "geom:groupId5.msg" "geom:lambert5SG.gn" -na;
connectAttr "geom:pTorus1Shape.iog.og[0]" "geom:lambert5SG.dsm" -na;
connectAttr "geom:lambert5SG.msg" "geom:materialInfo3.sg";
connectAttr "geom:lambert5SG1.msg" "geom:materialInfo3.m";
connectAttr "geom:lambert3SG1.oc" "geom:lambert3SG.ss";
connectAttr "geom:groupId6.msg" "geom:lambert3SG.gn" -na;
connectAttr "geom:pCube1Shape.iog.og[0]" "geom:lambert3SG.dsm" -na;
connectAttr "geom:lambert3SG.msg" "geom:materialInfo4.sg";
connectAttr "geom:lambert3SG1.msg" "geom:materialInfo4.m";
connectAttr "locator6_MKR.iog" "collection1.dsm" -na;
connectAttr "locator8_MKR.iog" "collection1.dsm" -na;
connectAttr "locator7_MKR.iog" "collection1.dsm" -na;
connectAttr "locator5_MKR.iog" "collection1.dsm" -na;
connectAttr "locator3_MKR.iog" "collection1.dsm" -na;
connectAttr "locator2_MKR.iog" "collection1.dsm" -na;
connectAttr "locator4_MKR.iog" "collection1.dsm" -na;
connectAttr "locator1_MKR.iog" "collection1.dsm" -na;
connectAttr "pCube1_locator9_MKR.iog" "collection1.dsm" -na;
connectAttr "pCube1_locator10_MKR.iog" "collection1.dsm" -na;
connectAttr "pCube1_locator11_MKR.iog" "collection1.dsm" -na;
connectAttr "pCube1_locator12_MKR.iog" "collection1.dsm" -na;
connectAttr "camera1.rz" "collection1.dnsm" -na;
connectAttr "camera1.ry" "collection1.dnsm" -na;
connectAttr "camera1.rx" "collection1.dnsm" -na;
connectAttr "camera1.tz" "collection1.dnsm" -na;
connectAttr "camera1.ty" "collection1.dnsm" -na;
connectAttr "camera1.tx" "collection1.dnsm" -na;
connectAttr "bundle10_BND.tz" "collection1.dnsm" -na;
connectAttr "bundle10_BND.ty" "collection1.dnsm" -na;
connectAttr "bundle10_BND.tx" "collection1.dnsm" -na;
connectAttr "lambert2SG.pa" ":renderPartition.st" -na;
connectAttr "lambert3SG.pa" ":renderPartition.st" -na;
connectAttr "lambert4SG.pa" ":renderPartition.st" -na;
connectAttr "lambert5SG.pa" ":renderPartition.st" -na;
connectAttr "geom:lambert2SG.pa" ":renderPartition.st" -na;
connectAttr "geom:lambert4SG.pa" ":renderPartition.st" -na;
connectAttr "geom:lambert5SG.pa" ":renderPartition.st" -na;
connectAttr "geom:lambert3SG.pa" ":renderPartition.st" -na;
connectAttr "lambert2.msg" ":defaultShaderList1.s" -na;
connectAttr "lambert3.msg" ":defaultShaderList1.s" -na;
connectAttr "lambert4.msg" ":defaultShaderList1.s" -na;
connectAttr "lambert5.msg" ":defaultShaderList1.s" -na;
connectAttr "geom:lambert2SG1.msg" ":defaultShaderList1.s" -na;
connectAttr "geom:lambert4SG1.msg" ":defaultShaderList1.s" -na;
connectAttr "geom:lambert5SG1.msg" ":defaultShaderList1.s" -na;
connectAttr "geom:lambert3SG1.msg" ":defaultShaderList1.s" -na;
connectAttr "place2dTexture1.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "place2dTexture2.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "place2dTexture3.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "place2dTexture4.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "checker1.msg" ":defaultTextureList1.tx" -na;
connectAttr "checker2.msg" ":defaultTextureList1.tx" -na;
connectAttr "checker3.msg" ":defaultTextureList1.tx" -na;
connectAttr "checker4.msg" ":defaultTextureList1.tx" -na;
// End of mmSolverBasicSolveA_badSolve01.ma
