//Maya ASCII 2017ff05 scene
//Name: rigHierarchy.ma
//Last modified: Sun, Jul 28, 2019 03:49:54 PM
//Codeset: UTF-8
requires maya "2017ff05";
requires -nodeType "mmMarkerScale" -nodeType "mmMarkerGroupTransform" "mmSolver" "0.3.0";
requires "stereoCamera" "10.0";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2017";
fileInfo "version" "2017";
fileInfo "cutIdentifier" "201710312130-1018716";
fileInfo "osv" "Linux 3.10.0-957.21.3.el7.x86_64 #1 SMP Tue Jun 18 16:35:19 UTC 2019 x86_64";
createNode transform -s -n "persp";
	rename -uid "24566900-0000-06C4-5D33-A82100000228";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -17.323812531587155 113.60505899482231 286.77766563031014 ;
	setAttr ".r" -type "double3" -3.3383527296032787 -6.19999999999989 -4.9988551737954488e-17 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "24566900-0000-06C4-5D33-A82100000229";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 311.0016785588046;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".tp" -type "double3" 0 -1.9721522630525295e-31 3.5527136788005009e-15 ;
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "24566900-0000-06C4-5D33-A8210000022A";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "24566900-0000-06C4-5D33-A8210000022B";
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
	rename -uid "24566900-0000-06C4-5D33-A8210000022C";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "24566900-0000-06C4-5D33-A8210000022D";
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
	rename -uid "24566900-0000-06C4-5D33-A8210000022E";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "24566900-0000-06C4-5D33-A8210000022F";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "persp1";
	rename -uid "24566900-0000-06C4-5D33-A86A000012B9";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode camera -n "perspShape2" -p "persp1";
	rename -uid "24566900-0000-06C4-5D33-A86A000012BA";
	setAttr -k off ".v";
	setAttr ".rnd" no;
	setAttr ".pze" yes;
	setAttr ".pn" -type "double2" 0.023582521689048248 0.09065245568089994 ;
	setAttr ".zom" 0.78998641845957362;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 123.92336363624474;
	setAttr ".imn" -type "string" "persp1";
	setAttr ".den" -type "string" "persp1_depth";
	setAttr ".man" -type "string" "persp1_mask";
	setAttr ".tp" -type "double3" 7.1054273576010019e-15 83.615858590122073 15.323332071137383 ;
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode mmMarkerGroupTransform -n "markerGroup1" -p "persp1";
	rename -uid "24566900-0000-06C4-5D33-A89A000012CC";
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
createNode transform -n "marker1_MKR" -p "markerGroup1";
	rename -uid "24566900-0000-06C4-5D33-A89A000012CA";
	addAttr -ci true -k true -sn "enable" -ln "enable" -dv 1 -min 0 -max 1 -at "short";
	addAttr -ci true -k true -sn "weight" -ln "weight" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "deviation" -ln "deviation" -dv -1 -min -1 -at "double";
	addAttr -s false -ci true -sn "bundle" -ln "bundle" -at "message";
	addAttr -ci true -sn "markerName" -ln "markerName" -dt "string";
	addAttr -ci true -sn "markerId" -ln "markerId" -dv -1 -at "long";
	setAttr ".t" -type "double3" 0.14351810189896197 0.16640909292722647 -1 ;
	setAttr -l on -k off ".tz";
	setAttr -av ".tx";
	setAttr -av ".ty";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -l on ".shxy";
	setAttr -l on ".shxz";
	setAttr -l on ".shyz";
	setAttr -l on -k on ".deviation";
	setAttr -l on ".markerName";
createNode locator -n "marker1_MKRShape" -p "marker1_MKR";
	rename -uid "24566900-0000-06C4-5D33-A89A000012CB";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 1 0 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 0.01 0.01 0 ;
	setAttr -l on ".lsz";
createNode transform -n "rig:Group";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000311";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:Main" -p "rig:Group";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000312";
	addAttr -ci true -sn "fkVis" -ln "fkVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "ikVis" -ln "ikVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "fkIkVis" -ln "fkIkVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "aimVis" -ln "aimVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "aimFKVis" -ln "aimFKVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "aimLRVis" -ln "aimLRVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "fingerVis" -ln "fingerVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "bendVis" -ln "bendVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "arrowVis" -ln "arrowVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "drvSysVis" -ln "drvSysVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "height" -ln "height" -at "double";
	addAttr -ci true -sn "version" -ln "version" -at "double";
	setAttr -cb on ".fkVis";
	setAttr -cb on ".ikVis";
	setAttr -cb on ".fkIkVis";
	setAttr -cb on ".aimVis";
	setAttr -cb on ".aimFKVis";
	setAttr -cb on ".aimLRVis";
	setAttr -cb on ".fingerVis";
	setAttr -cb on ".bendVis";
	setAttr -cb on ".arrowVis";
	setAttr -cb on ".drvSysVis";
	setAttr -l on ".height" 160.98089519875731;
	setAttr -l on ".version" 5.15;
createNode nurbsCurve -n "rig:MainShape" -p "rig:Main";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000313";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 15;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		21.058703739999999 1.2894737060000001e-15 -21.058703739999999
		-3.3977135570000001e-15 1.823591204e-15 -29.781504429999998
		-21.058703739999999 1.2894737060000001e-15 -21.058703739999999
		-29.781504429999998 5.2843110819999996e-31 -8.6299349089999998e-15
		-21.058703739999999 -1.2894737060000001e-15 21.058703739999999
		-8.9737485040000003e-15 -1.823591204e-15 29.781504429999998
		21.058703739999999 -1.2894737060000001e-15 21.058703739999999
		29.781504429999998 -9.7945439280000005e-31 1.5995704119999998e-14
		21.058703739999999 1.2894737060000001e-15 -21.058703739999999
		-3.3977135570000001e-15 1.823591204e-15 -29.781504429999998
		-21.058703739999999 1.2894737060000001e-15 -21.058703739999999
		;
createNode transform -n "rig:MotionSystem" -p "rig:Main";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000344";
createNode transform -n "rig:FKSystem" -p "rig:MotionSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000345";
createNode parentConstraint -n "rig:FKSystem_parentConstraint1" -p "rig:FKSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000346";
	addAttr -ci true -k true -sn "w0" -ln "RootZeroXformW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode transform -n "rig:FKParentConstraintToRoot_M" -p "rig:FKSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000359";
createNode parentConstraint -n "rig:FKParentConstraintToRoot_M_parentConstraint1" 
		-p "rig:FKParentConstraintToRoot_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000035A";
	addAttr -ci true -k true -sn "w0" -ln "LegLockConstrainedW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 1.7655691145602508e-15 88.867637422588331 0.47329046439254197 ;
	setAttr -k on ".w0";
createNode joint -n "rig:FKOffsetHip_R" -p "rig:FKParentConstraintToRoot_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000035B";
	setAttr ".t" -type "double3" -8.8414397624647592 -7.2524645691374872 -2.3750554043156038 ;
	setAttr ".r" -type "double3" 3.2284396665918145 -95.068695671171767 -89.197699744631521 ;
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode transform -n "rig:FKExtraHip_R" -p "rig:FKOffsetHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000035C";
	setAttr -l on -k off ".v";
	setAttr ".ro" 2;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKHip_R" -p "rig:FKExtraHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000035D";
	setAttr ".ro" 2;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKHip_RShape" -p "rig:FKHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000035E";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		0 -9.1605361250000001 -9.1605361250000001
		1.4210854720000001e-14 -9.0968899079999996e-15 -12.954954430000001
		2.842170943e-14 9.1605361250000001 -9.1605361250000001
		2.842170943e-14 12.954954430000001 -3.641531521e-14
		2.842170943e-14 9.1605361250000001 9.1605361250000001
		0 9.9989461160000007e-15 12.954954430000001
		-2.842170943e-14 -9.1605361250000001 9.1605361250000001
		0 -12.954954430000001 -8.8817841969999996e-15
		0 -9.1605361250000001 -9.1605361250000001
		1.4210854720000001e-14 -9.0968899079999996e-15 -12.954954430000001
		2.842170943e-14 9.1605361250000001 -9.1605361250000001
		;
createNode joint -n "rig:FKXHip_R" -p "rig:FKHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000035F";
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetKnee_R" -p "rig:FKXHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000360";
	setAttr ".t" -type "double3" 37.317101639277453 1.6202317265623378e-14 -2.7178259642823832e-13 ;
	setAttr ".r" -type "double3" 3.2284396665918176 -95.068695671171767 -97.103433474724156 ;
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 32.555966007969488 96.007269630534708 121.61073215270164 ;
	setAttr ".ds" 2;
createNode transform -n "rig:FKExtraKnee_R" -p "rig:FKOffsetKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000361";
	setAttr -l on -k off ".v";
	setAttr ".ro" 2;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKKnee_R" -p "rig:FKExtraKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000362";
	setAttr ".ro" 2;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKKnee_RShape" -p "rig:FKKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000363";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-1.4210854720000001e-14 -6.3176111209999997 -6.3176111209999997
		-2.842170943e-14 2.6645352589999999e-15 -8.9344513289999998
		-2.842170943e-14 6.3176111209999997 -6.3176111209999997
		-3.5527136790000001e-14 8.9344513289999998 2.842170943e-14
		-3.5527136790000001e-14 6.3176111209999997 6.3176111209999997
		-2.131628207e-14 -7.1054273579999998e-15 8.9344513289999998
		-2.842170943e-14 -6.3176111209999997 6.3176111209999997
		-3.5527136790000001e-14 -8.9344513289999998 2.131628207e-14
		-1.4210854720000001e-14 -6.3176111209999997 -6.3176111209999997
		-2.842170943e-14 2.6645352589999999e-15 -8.9344513289999998
		-2.842170943e-14 6.3176111209999997 -6.3176111209999997
		;
createNode joint -n "rig:FKXKnee_R" -p "rig:FKKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000364";
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetAnkle_R" -p "rig:FKXKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000365";
	setAttr ".t" -type "double3" 37.335576807429959 -1.3233858453531866e-13 1.9539925233402755e-14 ;
	setAttr ".r" -type "double3" 101.00958441533641 0 -89.999999999999332 ;
	setAttr ".ro" 3;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 32.555966007969367 96.007269630534651 129.51646588279399 ;
	setAttr ".ds" 2;
createNode transform -n "rig:FKExtraAnkle_R" -p "rig:FKOffsetAnkle_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000366";
	setAttr -l on -k off ".v";
	setAttr ".ro" 3;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKAnkle_R" -p "rig:FKExtraAnkle_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000367";
	setAttr ".ro" 3;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKAnkle_RShape" -p "rig:FKAnkle_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000368";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		5.8619775700000006e-14 -3.8958601910000001 -3.8958601910000001
		6.1284310959999999e-14 -3.5527136789999999e-15 -5.5095783190000001
		6.2172489380000005e-14 3.8958601910000001 -3.8958601910000001
		5.8619775700000006e-14 5.5095783190000001 7.904787935e-14
		5.5955240440000001e-14 3.8958601910000001 3.8958601910000001
		5.4178883600000001e-14 5.3290705179999997e-15 5.5095783190000001
		5.3290705180000002e-14 -3.8958601910000001 3.8958601910000001
		5.773159728e-14 -5.5095783190000001 8.9706020389999996e-14
		5.8619775700000006e-14 -3.8958601910000001 -3.8958601910000001
		6.1284310959999999e-14 -3.5527136789999999e-15 -5.5095783190000001
		6.2172489380000005e-14 3.8958601910000001 -3.8958601910000001
		;
createNode joint -n "rig:FKXAnkle_R" -p "rig:FKAnkle_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000369";
	setAttr ".ro" 3;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode transform -n "rig:AlignIKToAnkle_R" -p "rig:FKXAnkle_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000036A";
	setAttr ".r" -type "double3" -90.000000000003581 89.999999999999332 -11.009584415336402 ;
	setAttr ".ro" 3;
	setAttr ".s" -type "double3" 0.99999999999999989 1 0.99999999999999978 ;
createNode joint -n "rig:FKOffsetHip_L" -p "rig:FKParentConstraintToRoot_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000036B";
	setAttr ".t" -type "double3" 8.8414397624647449 -7.2524645691374872 -2.3750554043156038 ;
	setAttr ".r" -type "double3" -3.2284396665917221 -84.931304328828261 90.80230025536838 ;
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode transform -n "rig:FKExtraHip_L" -p "rig:FKOffsetHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000036C";
	setAttr -l on -k off ".v";
	setAttr ".ro" 2;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKHip_L" -p "rig:FKExtraHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000036D";
	setAttr ".ro" 2;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKHip_LShape" -p "rig:FKHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000036E";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-1.4210854720000001e-14 9.1605361250000001 9.1605361250000001
		0 -2.2135071550000001e-15 12.954954430000001
		0 -9.1605361250000001 9.1605361250000001
		0 -12.954954430000001 4.4408920990000004e-15
		0 -9.1605361250000001 -9.1605361250000001
		0 -3.9898639949999998e-15 -12.954954430000001
		1.4210854720000001e-14 9.1605361250000001 -9.1605361250000001
		-1.4210854720000001e-14 12.954954430000001 -7.1054273579999998e-15
		-1.4210854720000001e-14 9.1605361250000001 9.1605361250000001
		0 -2.2135071550000001e-15 12.954954430000001
		0 -9.1605361250000001 9.1605361250000001
		;
createNode joint -n "rig:FKXHip_L" -p "rig:FKHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000036F";
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetKnee_L" -p "rig:FKXHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000370";
	setAttr ".t" -type "double3" -37.317101639277432 -9.9253938401488995e-14 2.8332891588433995e-13 ;
	setAttr ".r" -type "double3" -3.2284396665917154 -84.931304328828276 82.896566525275674 ;
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 32.555966007969005 83.992730369465363 -58.389267847298797 ;
	setAttr ".ds" 2;
createNode transform -n "rig:FKExtraKnee_L" -p "rig:FKOffsetKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000371";
	setAttr -l on -k off ".v";
	setAttr ".ro" 2;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKKnee_L" -p "rig:FKExtraKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000372";
	setAttr ".ro" 2;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKKnee_LShape" -p "rig:FKKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000373";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		1.4210854720000001e-14 6.3176111209999997 6.3176111209999997
		1.4210854720000001e-14 -8.881784197e-16 8.9344513289999998
		1.4210854720000001e-14 -6.3176111209999997 6.3176111209999997
		1.4210854720000001e-14 -8.9344513289999998 1.776356839e-15
		7.1054273579999998e-15 -6.3176111209999997 -6.3176111209999997
		0 -2.6645352589999999e-15 -8.9344513289999998
		1.4210854720000001e-14 6.3176111209999997 -6.3176111209999997
		1.4210854720000001e-14 8.9344513289999998 -4.4408920990000004e-15
		1.4210854720000001e-14 6.3176111209999997 6.3176111209999997
		1.4210854720000001e-14 -8.881784197e-16 8.9344513289999998
		1.4210854720000001e-14 -6.3176111209999997 6.3176111209999997
		;
createNode joint -n "rig:FKXKnee_L" -p "rig:FKKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000374";
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetAnkle_L" -p "rig:FKXKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000375";
	setAttr ".t" -type "double3" -37.335576807430002 -1.3322676295501878e-14 6.2172489379008766e-15 ;
	setAttr ".r" -type "double3" -78.990415584663666 0 89.999999999999375 ;
	setAttr ".ro" 3;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 32.555966007969204 83.992730369465392 -50.483534117206325 ;
	setAttr ".ds" 2;
createNode transform -n "rig:FKExtraAnkle_L" -p "rig:FKOffsetAnkle_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000376";
	setAttr -l on -k off ".v";
	setAttr ".ro" 3;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKAnkle_L" -p "rig:FKExtraAnkle_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000377";
	setAttr ".ro" 3;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKAnkle_LShape" -p "rig:FKAnkle_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000378";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		0 3.8958601910000001 3.8958601910000001
		-8.881784197e-16 1.776356839e-15 5.5095783190000001
		-8.881784197e-16 -3.8958601910000001 3.8958601910000001
		1.776356839e-15 -5.5095783190000001 1.776356839e-15
		8.881784197e-16 -3.8958601910000001 -3.8958601910000001
		8.881784197e-16 0 -5.5095783190000001
		8.881784197e-16 3.8958601910000001 -3.8958601910000001
		-2.6645352589999999e-15 5.5095783190000001 -2.6645352589999999e-15
		0 3.8958601910000001 3.8958601910000001
		-8.881784197e-16 1.776356839e-15 5.5095783190000001
		-8.881784197e-16 -3.8958601910000001 3.8958601910000001
		;
createNode joint -n "rig:FKXAnkle_L" -p "rig:FKAnkle_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000379";
	setAttr ".ro" 3;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode transform -n "rig:AlignIKToAnkle_L" -p "rig:FKXAnkle_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000037A";
	setAttr ".r" -type "double3" 89.999999999996717 89.999999999999375 -11.009584415336333 ;
	setAttr ".ro" 3;
createNode transform -n "rig:FKParentConstraintToWrist_R" -p "rig:FKSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000037B";
createNode parentConstraint -n "rig:FKParentConstraintToWrist_R_parentConstraint1" 
		-p "rig:FKParentConstraintToWrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000037C";
	addAttr -ci true -k true -sn "w0" -ln "Wrist_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 31.800941854946188 50.083889543113798 114.13207475105105 ;
	setAttr ".rst" -type "double3" -20.987722480873064 78.841785267578885 1.9132525377466347 ;
	setAttr ".rsrr" -type "double3" 83.562187684236775 -32.690834179111995 -93.414234120871384 ;
	setAttr -k on ".w0";
createNode joint -n "rig:FKOffsetIndexFinger1_R" -p "rig:FKParentConstraintToWrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000037D";
	setAttr ".t" -type "double3" 9.0507967385055395 7.1054273576010019e-15 -7.815970093361102e-14 ;
	setAttr ".r" -type "double3" 6.8485650458619505 -62.024420297785454 -63.738870129781482 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 51.733832014335718 81.235819171498221 109.20479172099506 ;
	setAttr ".ds" 2;
createNode transform -n "rig:SDK1FKIndexFinger1_R" -p "rig:FKOffsetIndexFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000037E";
	setAttr ".ro" 5;
createNode transform -n "rig:SDK2FKIndexFinger1_R" -p "rig:SDK1FKIndexFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000037F";
	setAttr ".ro" 5;
createNode transform -n "rig:FKExtraIndexFinger1_R" -p "rig:SDK2FKIndexFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000380";
	setAttr -l on -k off ".v";
	setAttr ".ro" 5;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKIndexFinger1_R" -p "rig:FKExtraIndexFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000381";
	setAttr ".ro" 5;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKIndexFinger1_RShape" -p "rig:FKIndexFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000382";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-1.847411113e-13 -1.2635222239999999 -1.2635222239999999
		-1.847411113e-13 4.9737991500000003e-14 -1.7868902659999999
		-1.7053025659999999e-13 1.2635222239999999 -1.2635222239999999
		-1.847411113e-13 1.7868902659999999 2.7711166689999998e-13
		-1.847411113e-13 1.2635222239999999 1.2635222239999999
		-1.847411113e-13 4.6185277819999998e-14 1.7868902659999999
		-1.847411113e-13 -1.2635222239999999 1.2635222239999999
		-1.7053025659999999e-13 -1.7868902659999999 2.5934809860000001e-13
		-1.847411113e-13 -1.2635222239999999 -1.2635222239999999
		-1.847411113e-13 4.9737991500000003e-14 -1.7868902659999999
		-1.7053025659999999e-13 1.2635222239999999 -1.2635222239999999
		;
createNode joint -n "rig:FKXIndexFinger1_R" -p "rig:FKIndexFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000383";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetIndexFinger2_R" -p "rig:FKXIndexFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000384";
	setAttr ".t" -type "double3" 2.615071168114838 1.7763568394002505e-14 3.5527136788005009e-14 ;
	setAttr ".r" -type "double3" 41.221364032841194 -43.833979375356691 -35.65413487247406 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -6.8485650458619443 62.024420297785454 63.738870129781453 ;
	setAttr ".ds" 2;
createNode transform -n "rig:SDK1FKIndexFinger2_R" -p "rig:FKOffsetIndexFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000385";
	setAttr ".ro" 5;
createNode transform -n "rig:FKExtraIndexFinger2_R" -p "rig:SDK1FKIndexFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000386";
	setAttr -l on -k off ".v";
	setAttr ".ro" 5;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKIndexFinger2_R" -p "rig:FKExtraIndexFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000387";
	setAttr ".ro" 5;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKIndexFinger2_RShape" -p "rig:FKIndexFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000388";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-1.2789769239999999e-13 -1.2635222239999999 -1.2635222239999999
		-1.2789769239999999e-13 7.1054273580000001e-14 -1.7868902659999999
		-1.2789769239999999e-13 1.2635222239999999 -1.2635222239999999
		-1.421085472e-13 1.7868902659999999 2.842170943e-13
		-1.421085472e-13 1.2635222239999999 1.2635222239999999
		-1.421085472e-13 8.1712414610000005e-14 1.7868902659999999
		-1.136868377e-13 -1.2635222239999999 1.2635222239999999
		-1.2789769239999999e-13 -1.7868902659999999 2.6467716910000001e-13
		-1.2789769239999999e-13 -1.2635222239999999 -1.2635222239999999
		-1.2789769239999999e-13 7.1054273580000001e-14 -1.7868902659999999
		-1.2789769239999999e-13 1.2635222239999999 -1.2635222239999999
		;
createNode joint -n "rig:FKXIndexFinger2_R" -p "rig:FKIndexFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000389";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetIndexFinger3_R" -p "rig:FKXIndexFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000038A";
	setAttr ".t" -type "double3" 2.2798674841394302 1.0658141036401503e-14 -6.5725203057809267e-14 ;
	setAttr ".r" -type "double3" 43.84641971513129 -38.134697599451172 -34.081157478973147 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -41.221364032841208 43.833979375356691 35.654134872474089 ;
	setAttr ".ds" 2;
createNode transform -n "rig:SDK1FKIndexFinger3_R" -p "rig:FKOffsetIndexFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000038B";
	setAttr ".ro" 5;
createNode transform -n "rig:FKExtraIndexFinger3_R" -p "rig:SDK1FKIndexFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000038C";
	setAttr -l on -k off ".v";
	setAttr ".ro" 5;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKIndexFinger3_R" -p "rig:FKExtraIndexFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000038D";
	setAttr ".ro" 5;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKIndexFinger3_RShape" -p "rig:FKIndexFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000038E";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-2.4158453019999999e-13 -1.2635222239999999 -1.2635222239999999
		-2.5579538489999998e-13 9.2370555650000001e-14 -1.7868902659999999
		-2.6290081219999999e-13 1.2635222239999999 -1.2635222239999999
		-2.7000623960000001e-13 1.7868902659999999 1.740829703e-13
		-2.7000623960000001e-13 1.2635222239999999 1.2635222239999999
		-2.7000623960000001e-13 8.5265128290000004e-14 1.7868902659999999
		-2.6290081219999999e-13 -1.2635222239999999 1.2635222239999999
		-2.4868995750000001e-13 -1.7868902659999999 1.740829703e-13
		-2.4158453019999999e-13 -1.2635222239999999 -1.2635222239999999
		-2.5579538489999998e-13 9.2370555650000001e-14 -1.7868902659999999
		-2.6290081219999999e-13 1.2635222239999999 -1.2635222239999999
		;
createNode joint -n "rig:FKXIndexFinger3_R" -p "rig:FKIndexFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000038F";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetMiddleFinger1_R" -p "rig:FKParentConstraintToWrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000390";
	setAttr ".t" -type "double3" 8.7083736116588426 -1.9121430819272192 0.57542589341596084 ;
	setAttr ".r" -type "double3" 41.187147339794279 -65.746138776691623 -32.972447854481295 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 51.733832014335718 81.235819171498221 109.20479172099506 ;
	setAttr ".ds" 2;
createNode transform -n "rig:SDK1FKMiddleFinger1_R" -p "rig:FKOffsetMiddleFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000391";
	setAttr ".ro" 5;
createNode transform -n "rig:FKExtraMiddleFinger1_R" -p "rig:SDK1FKMiddleFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000392";
	setAttr -l on -k off ".v";
	setAttr ".ro" 5;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKMiddleFinger1_R" -p "rig:FKExtraMiddleFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000393";
	setAttr ".ro" 5;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKMiddleFinger1_RShape" -p "rig:FKMiddleFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000394";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-2.131628207e-13 -1.2635222239999999 -1.2635222239999999
		-1.9895196600000001e-13 1.2789769239999999e-13 -1.7868902659999999
		-2.2737367540000001e-13 1.2635222239999999 -1.2635222239999999
		-2.2737367540000001e-13 1.7868902659999999 2.2870594309999999e-13
		-2.5579538489999998e-13 1.2635222239999999 1.2635222239999999
		-2.2737367540000001e-13 1.2079226509999999e-13 1.7868902659999999
		-2.2737367540000001e-13 -1.2635222239999999 1.2635222239999999
		-2.2737367540000001e-13 -1.7868902659999999 2.1449508840000001e-13
		-2.131628207e-13 -1.2635222239999999 -1.2635222239999999
		-1.9895196600000001e-13 1.2789769239999999e-13 -1.7868902659999999
		-2.2737367540000001e-13 1.2635222239999999 -1.2635222239999999
		;
createNode joint -n "rig:FKXMiddleFinger1_R" -p "rig:FKMiddleFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000395";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetMiddleFinger2_R" -p "rig:FKXMiddleFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000396";
	setAttr ".t" -type "double3" 2.9299735768954065 -1.0658141036401503e-14 4.4408920985006262e-15 ;
	setAttr ".r" -type "double3" 61.064319754781437 -42.12931657099854 -18.42209280744293 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -41.187147339794251 65.746138776691623 32.972447854481331 ;
	setAttr ".ds" 2;
createNode transform -n "rig:SDK1FKMiddleFinger2_R" -p "rig:FKOffsetMiddleFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000397";
	setAttr ".ro" 5;
createNode transform -n "rig:FKExtraMiddleFinger2_R" -p "rig:SDK1FKMiddleFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000398";
	setAttr -l on -k off ".v";
	setAttr ".ro" 5;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKMiddleFinger2_R" -p "rig:FKExtraMiddleFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000399";
	setAttr ".ro" 5;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKMiddleFinger2_RShape" -p "rig:FKMiddleFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000039A";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-2.0605739340000003e-13 -1.2635222239999999 -1.2635222239999999
		-2.0605739340000003e-13 1.3855583349999999e-13 -1.7868902659999999
		-2.131628207e-13 1.2635222239999999 -1.2635222239999999
		-2.4158453019999999e-13 1.7868902659999999 1.847411113e-13
		-2.4158453019999999e-13 1.2635222239999999 1.2635222239999999
		-2.3447910280000002e-13 1.3855583349999999e-13 1.7868902659999999
		-2.2026824809999999e-13 -1.2635222239999999 1.2635222239999999
		-2.0605739340000003e-13 -1.7868902659999999 1.9184653869999999e-13
		-2.0605739340000003e-13 -1.2635222239999999 -1.2635222239999999
		-2.0605739340000003e-13 1.3855583349999999e-13 -1.7868902659999999
		-2.131628207e-13 1.2635222239999999 -1.2635222239999999
		;
createNode joint -n "rig:FKXMiddleFinger2_R" -p "rig:FKMiddleFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000039B";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetMiddleFinger3_R" -p "rig:FKXMiddleFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000039C";
	setAttr ".t" -type "double3" 2.3283439685011444 -3.5527136788005009e-15 -1.7763568394002505e-14 ;
	setAttr ".r" -type "double3" 66.452821474085255 -27.683798470919989 -15.303978594248667 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -61.064319754781451 42.12931657099854 18.422092807442933 ;
	setAttr ".ds" 2;
createNode transform -n "rig:SDK1FKMiddleFinger3_R" -p "rig:FKOffsetMiddleFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000039D";
	setAttr ".ro" 5;
createNode transform -n "rig:FKExtraMiddleFinger3_R" -p "rig:SDK1FKMiddleFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000039E";
	setAttr -l on -k off ".v";
	setAttr ".ro" 5;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKMiddleFinger3_R" -p "rig:FKExtraMiddleFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000039F";
	setAttr ".ro" 5;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKMiddleFinger3_RShape" -p "rig:FKMiddleFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003A0";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-3.4106051319999998e-13 -1.2635222239999999 -1.2635222239999999
		-3.481659405e-13 1.10134124e-13 -1.7868902659999999
		-3.4106051319999998e-13 1.2635222239999999 -1.2635222239999999
		-3.7658765000000002e-13 1.7868902659999999 7.1054273580000001e-14
		-3.6237679519999999e-13 1.2635222239999999 1.2635222239999999
		-3.481659405e-13 1.136868377e-13 1.7868902659999999
		-3.5527136790000002e-13 -1.2635222239999999 1.2635222239999999
		-3.3395508580000002e-13 -1.7868902659999999 1.065814104e-13
		-3.4106051319999998e-13 -1.2635222239999999 -1.2635222239999999
		-3.481659405e-13 1.10134124e-13 -1.7868902659999999
		-3.4106051319999998e-13 1.2635222239999999 -1.2635222239999999
		;
createNode joint -n "rig:FKXMiddleFinger3_R" -p "rig:FKMiddleFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003A1";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetCup_R" -p "rig:FKParentConstraintToWrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003A2";
	setAttr ".t" -type "double3" 2.5323556682531532 -1.7906199654992676 0.35330912270254444 ;
	setAttr ".r" -type "double3" 85.778524604137147 -23.762614689202291 -97.599241183507019 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 51.733832014335718 81.235819171498221 109.20479172099506 ;
	setAttr ".ds" 2;
createNode transform -n "rig:SDK1FKCup_R" -p "rig:FKOffsetCup_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003A3";
createNode transform -n "rig:FKExtraCup_R" -p "rig:SDK1FKCup_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003A4";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKCup_R" -p "rig:FKExtraCup_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003A5";
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKCup_RShape" -p "rig:FKCup_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003A6";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-1.847411113e-13 -1.2635222239999999 -1.2635222239999999
		-1.847411113e-13 2.842170943e-13 -1.7868902659999999
		-1.9895196600000001e-13 1.2635222239999999 -1.2635222239999999
		-1.847411113e-13 1.7868902659999999 2.1671553440000001e-13
		-2.2737367540000001e-13 1.2635222239999999 1.2635222239999999
		-1.847411113e-13 2.7711166689999998e-13 1.7868902659999999
		-1.7053025659999999e-13 -1.2635222239999999 1.2635222239999999
		-1.847411113e-13 -1.7868902659999999 1.9895196600000001e-13
		-1.847411113e-13 -1.2635222239999999 -1.2635222239999999
		-1.847411113e-13 2.842170943e-13 -1.7868902659999999
		-1.9895196600000001e-13 1.2635222239999999 -1.2635222239999999
		;
createNode joint -n "rig:FKXCup_R" -p "rig:FKCup_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003A7";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetPinkyFinger1_R" -p "rig:FKXCup_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003A8";
	setAttr ".t" -type "double3" 4.5250926779440093 -2.3533218848592128 -0.44446663353526361 ;
	setAttr ".r" -type "double3" 136.50375136469935 -67.812893173651602 50.272110162251074 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 67.329008883442611 79.933484765316663 133.82335704739231 ;
	setAttr ".ds" 2;
createNode transform -n "rig:SDK1FKPinkyFinger1_R" -p "rig:FKOffsetPinkyFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003A9";
	setAttr ".ro" 5;
createNode transform -n "rig:SDK2FKPinkyFinger1_R" -p "rig:SDK1FKPinkyFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003AA";
	setAttr ".ro" 5;
createNode transform -n "rig:FKExtraPinkyFinger1_R" -p "rig:SDK2FKPinkyFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003AB";
	setAttr -l on -k off ".v";
	setAttr ".ro" 5;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKPinkyFinger1_R" -p "rig:FKExtraPinkyFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003AC";
	setAttr ".ro" 5;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKPinkyFinger1_RShape" -p "rig:FKPinkyFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003AD";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-2.9842794899999998e-13 -1.2635222239999999 -1.2635222239999999
		-3.1263880370000002e-13 2.4691360069999999e-13 -1.7868902659999999
		-3.268496584e-13 1.2635222239999999 -1.2635222239999999
		-3.4106051319999998e-13 1.7868902659999999 1.6942003359999999e-13
		-3.1263880370000002e-13 1.2635222239999999 1.2635222239999999
		-2.9842794899999998e-13 2.3980817329999997e-13 1.7868902659999999
		-2.9842794899999998e-13 -1.2635222239999999 1.2635222239999999
		-2.842170943e-13 -1.7868902659999999 1.7075230120000001e-13
		-2.9842794899999998e-13 -1.2635222239999999 -1.2635222239999999
		-3.1263880370000002e-13 2.4691360069999999e-13 -1.7868902659999999
		-3.268496584e-13 1.2635222239999999 -1.2635222239999999
		;
createNode joint -n "rig:FKXPinkyFinger1_R" -p "rig:FKPinkyFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003AE";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetPinkyFinger2_R" -p "rig:FKXPinkyFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003AF";
	setAttr ".t" -type "double3" 2.1075383328535224 -1.9539925233402755e-14 3.5083047578154947e-14 ;
	setAttr ".r" -type "double3" 109.18944600847669 -48.876650366371202 26.562408986809672 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -136.50375136469947 67.812893173651588 -50.27211016225116 ;
	setAttr ".ds" 2;
createNode transform -n "rig:SDK1FKPinkyFinger2_R" -p "rig:FKOffsetPinkyFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003B0";
	setAttr ".ro" 5;
createNode transform -n "rig:FKExtraPinkyFinger2_R" -p "rig:SDK1FKPinkyFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003B1";
	setAttr -l on -k off ".v";
	setAttr ".ro" 5;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKPinkyFinger2_R" -p "rig:FKExtraPinkyFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003B2";
	setAttr ".ro" 5;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKPinkyFinger2_RShape" -p "rig:FKPinkyFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003B3";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-2.4158453019999999e-13 -1.2635222239999999 -1.2635222239999999
		-2.7000623960000001e-13 2.6467716910000001e-13 -1.7868902659999999
		-2.5579538489999998e-13 1.2635222239999999 -1.2635222239999999
		-2.7000623960000001e-13 1.7868902659999999 7.8159700929999994e-14
		-2.5579538489999998e-13 1.2635222239999999 1.2635222239999999
		-2.4158453019999999e-13 2.5934809860000001e-13 1.7868902659999999
		-2.4158453019999999e-13 -1.2635222239999999 1.2635222239999999
		-2.4158453019999999e-13 -1.7868902659999999 8.1712414610000005e-14
		-2.4158453019999999e-13 -1.2635222239999999 -1.2635222239999999
		-2.7000623960000001e-13 2.6467716910000001e-13 -1.7868902659999999
		-2.5579538489999998e-13 1.2635222239999999 -1.2635222239999999
		;
createNode joint -n "rig:FKXPinkyFinger2_R" -p "rig:FKPinkyFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003B4";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetPinkyFinger3_R" -p "rig:FKXPinkyFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003B5";
	setAttr ".t" -type "double3" 1.5833293982734915 4.0856207306205761e-14 -8.8817841970012523e-14 ;
	setAttr ".r" -type "double3" 100.7393479702766 -28.79637685380785 21.546444006064778 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -109.18944600847671 48.876650366371244 -26.562408986809686 ;
	setAttr ".ds" 2;
createNode transform -n "rig:SDK1FKPinkyFinger3_R" -p "rig:FKOffsetPinkyFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003B6";
	setAttr ".ro" 5;
createNode transform -n "rig:FKExtraPinkyFinger3_R" -p "rig:SDK1FKPinkyFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003B7";
	setAttr -l on -k off ".v";
	setAttr ".ro" 5;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKPinkyFinger3_R" -p "rig:FKExtraPinkyFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003B8";
	setAttr ".ro" 5;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKPinkyFinger3_RShape" -p "rig:FKPinkyFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003B9";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-2.4158453019999999e-13 -1.2635222239999999 -1.2635222239999999
		-2.4868995750000001e-13 2.3980817329999997e-13 -1.7868902659999999
		-2.5579538489999998e-13 1.2635222239999999 -1.2635222239999999
		-2.4868995750000001e-13 1.7868902659999999 3.5527136790000001e-14
		-2.5579538489999998e-13 1.2635222239999999 1.2635222239999999
		-2.4868995750000001e-13 2.5046631440000002e-13 1.7868902659999999
		-2.3447910280000002e-13 -1.2635222239999999 1.2635222239999999
		-2.3447910280000002e-13 -1.7868902659999999 7.1054273579999998e-15
		-2.4158453019999999e-13 -1.2635222239999999 -1.2635222239999999
		-2.4868995750000001e-13 2.3980817329999997e-13 -1.7868902659999999
		-2.5579538489999998e-13 1.2635222239999999 -1.2635222239999999
		;
createNode joint -n "rig:FKXPinkyFinger3_R" -p "rig:FKPinkyFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003BA";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetRingFinger1_R" -p "rig:FKXCup_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003BB";
	setAttr ".t" -type "double3" 5.5468274631967844 -0.87121337525206144 0.085476270302692114 ;
	setAttr ".r" -type "double3" 74.019673835312631 -70.873777743924592 -4.511797831402486 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 67.329008883442611 79.933484765316663 133.82335704739231 ;
	setAttr ".ds" 2;
createNode transform -n "rig:SDK1FKRingFinger1_R" -p "rig:FKOffsetRingFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003BC";
	setAttr ".ro" 5;
createNode transform -n "rig:SDK2FKRingFinger1_R" -p "rig:SDK1FKRingFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003BD";
	setAttr ".ro" 5;
createNode transform -n "rig:FKExtraRingFinger1_R" -p "rig:SDK2FKRingFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003BE";
	setAttr -l on -k off ".v";
	setAttr ".ro" 5;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKRingFinger1_R" -p "rig:FKExtraRingFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003BF";
	setAttr ".ro" 5;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKRingFinger1_RShape" -p "rig:FKRingFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003C0";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-2.7000623960000001e-13 -1.2635222239999999 -1.2635222239999999
		-2.5579538489999998e-13 2.025046797e-13 -1.7868902659999999
		-2.7000623960000001e-13 1.2635222239999999 -1.2635222239999999
		-2.842170943e-13 1.7868902659999999 2.4669155609999998e-13
		-2.842170943e-13 1.2635222239999999 1.2635222239999999
		-2.842170943e-13 1.9895196600000001e-13 1.7868902659999999
		-2.7000623960000001e-13 -1.2635222239999999 1.2635222239999999
		-3.1263880370000002e-13 -1.7868902659999999 2.3775426070000002e-13
		-2.7000623960000001e-13 -1.2635222239999999 -1.2635222239999999
		-2.5579538489999998e-13 2.025046797e-13 -1.7868902659999999
		-2.7000623960000001e-13 1.2635222239999999 -1.2635222239999999
		;
createNode joint -n "rig:FKXRingFinger1_R" -p "rig:FKRingFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003C1";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetRingFinger2_R" -p "rig:FKXRingFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003C2";
	setAttr ".t" -type "double3" 2.5823924595557628 -7.1054273576010019e-15 -1.6320278461989801e-14 ;
	setAttr ".r" -type "double3" 76.400592326262341 -45.576761008370518 -2.5127317211375755 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -74.019673835312801 70.873777743924634 4.5117978314024558 ;
	setAttr ".ds" 2;
createNode transform -n "rig:SDK1FKRingFinger2_R" -p "rig:FKOffsetRingFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003C3";
	setAttr ".ro" 5;
createNode transform -n "rig:FKExtraRingFinger2_R" -p "rig:SDK1FKRingFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003C4";
	setAttr -l on -k off ".v";
	setAttr ".ro" 5;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKRingFinger2_R" -p "rig:FKExtraRingFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003C5";
	setAttr ".ro" 5;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKRingFinger2_RShape" -p "rig:FKRingFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003C6";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-2.2026824809999999e-13 -1.2635222239999999 -1.2635222239999999
		-2.2026824809999999e-13 1.847411113e-13 -1.7868902659999999
		-2.4868995750000001e-13 1.2635222239999999 -1.2635222239999999
		-2.4158453019999999e-13 1.7868902659999999 1.314504061e-13
		-2.4868995750000001e-13 1.2635222239999999 1.2635222239999999
		-2.4158453019999999e-13 1.9184653869999999e-13 1.7868902659999999
		-2.3447910280000002e-13 -1.2635222239999999 1.2635222239999999
		-2.2737367540000001e-13 -1.7868902659999999 1.3855583349999999e-13
		-2.2026824809999999e-13 -1.2635222239999999 -1.2635222239999999
		-2.2026824809999999e-13 1.847411113e-13 -1.7868902659999999
		-2.4868995750000001e-13 1.2635222239999999 -1.2635222239999999
		;
createNode joint -n "rig:FKXRingFinger2_R" -p "rig:FKRingFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003C7";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetRingFinger3_R" -p "rig:FKXRingFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003C8";
	setAttr ".t" -type "double3" 2.2923824975696405 2.1316282072803006e-14 3.1974423109204508e-14 ;
	setAttr ".r" -type "double3" 77.607857464779684 -35.960486479577945 -1.6652026971190463 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -76.400592326262327 45.576761008370518 2.5127317211375853 ;
	setAttr ".ds" 2;
createNode transform -n "rig:SDK1FKRingFinger3_R" -p "rig:FKOffsetRingFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003C9";
	setAttr ".ro" 5;
createNode transform -n "rig:FKExtraRingFinger3_R" -p "rig:SDK1FKRingFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003CA";
	setAttr -l on -k off ".v";
	setAttr ".ro" 5;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKRingFinger3_R" -p "rig:FKExtraRingFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003CB";
	setAttr ".ro" 5;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKRingFinger3_RShape" -p "rig:FKRingFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003CC";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-3.1974423109999998e-13 -1.2635222239999999 -1.2635222239999999
		-3.3395508580000002e-13 1.4566126080000001e-13 -1.7868902659999999
		-3.481659405e-13 1.2635222239999999 -1.2635222239999999
		-3.6237679519999999e-13 1.7868902659999999 2.131628207e-14
		-3.5527136790000002e-13 1.2635222239999999 1.2635222239999999
		-3.4106051319999998e-13 1.4921397449999999e-13 1.7868902659999999
		-3.268496584e-13 -1.2635222239999999 1.2635222239999999
		-3.268496584e-13 -1.7868902659999999 5.684341886e-14
		-3.1974423109999998e-13 -1.2635222239999999 -1.2635222239999999
		-3.3395508580000002e-13 1.4566126080000001e-13 -1.7868902659999999
		-3.481659405e-13 1.2635222239999999 -1.2635222239999999
		;
createNode joint -n "rig:FKXRingFinger3_R" -p "rig:FKRingFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003CD";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetThumbFinger1_R" -p "rig:FKParentConstraintToWrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003CE";
	setAttr ".t" -type "double3" 3.0055150379940727 0.51952218981555376 -1.7089693953339662 ;
	setAttr ".r" -type "double3" -39.229806998261225 8.580219918160374 -75.759765342310146 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 51.733832014335718 81.235819171498221 109.20479172099506 ;
	setAttr ".ds" 2;
createNode transform -n "rig:FKExtraThumbFinger1_R" -p "rig:FKOffsetThumbFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003CF";
	setAttr -l on -k off ".v";
	setAttr ".ro" 5;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKThumbFinger1_R" -p "rig:FKExtraThumbFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003D0";
	setAttr ".ro" 5;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKThumbFinger1_RShape" -p "rig:FKThumbFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003D1";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-2.131628207e-13 -1.2635222239999999 -1.2635222239999999
		-2.131628207e-13 -2.3803181650000001e-13 -1.7868902659999999
		-1.7763568390000001e-13 1.2635222239999999 -1.2635222239999999
		-1.9895196600000001e-13 1.7868902659999999 1.2079226509999999e-13
		-1.847411113e-13 1.2635222239999999 1.2635222239999999
		-2.2737367540000001e-13 -2.3447910280000002e-13 1.7868902659999999
		-2.2737367540000001e-13 -1.2635222239999999 1.2635222239999999
		-2.0605739340000003e-13 -1.7868902659999999 1.2079226509999999e-13
		-2.131628207e-13 -1.2635222239999999 -1.2635222239999999
		-2.131628207e-13 -2.3803181650000001e-13 -1.7868902659999999
		-1.7763568390000001e-13 1.2635222239999999 -1.2635222239999999
		;
createNode joint -n "rig:FKXThumbFinger1_R" -p "rig:FKThumbFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003D2";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetThumbFinger2_R" -p "rig:FKXThumbFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003D3";
	setAttr ".t" -type "double3" 4.0601659831538797 -3.5527136788005009e-15 6.3948846218409017e-14 ;
	setAttr ".r" -type "double3" -23.742857290015859 9.5767208242306356 -81.970613393999798 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 39.229806998261218 -8.5802199181603758 75.759765342310146 ;
	setAttr ".ds" 2;
createNode transform -n "rig:SDK1FKThumbFinger2_R" -p "rig:FKOffsetThumbFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003D4";
	setAttr ".ro" 5;
createNode transform -n "rig:FKExtraThumbFinger2_R" -p "rig:SDK1FKThumbFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003D5";
	setAttr -l on -k off ".v";
	setAttr ".ro" 5;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKThumbFinger2_R" -p "rig:FKExtraThumbFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003D6";
	setAttr ".ro" 5;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKThumbFinger2_RShape" -p "rig:FKThumbFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003D7";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-1.847411113e-13 -1.2635222239999999 -1.2635222239999999
		-1.847411113e-13 -2.6290081219999999e-13 -1.7868902659999999
		-1.7053025659999999e-13 1.2635222239999999 -1.2635222239999999
		-1.847411113e-13 1.7868902659999999 1.421085472e-13
		-1.847411113e-13 1.2635222239999999 1.2635222239999999
		-1.7053025659999999e-13 -2.8066438060000001e-13 1.7868902659999999
		-1.847411113e-13 -1.2635222239999999 1.2635222239999999
		-1.9895196600000001e-13 -1.7868902659999999 1.3855583349999999e-13
		-1.847411113e-13 -1.2635222239999999 -1.2635222239999999
		-1.847411113e-13 -2.6290081219999999e-13 -1.7868902659999999
		-1.7053025659999999e-13 1.2635222239999999 -1.2635222239999999
		;
createNode joint -n "rig:FKXThumbFinger2_R" -p "rig:FKThumbFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003D8";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetThumbFinger3_R" -p "rig:FKXThumbFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003D9";
	setAttr ".t" -type "double3" 2.1504736042850396 -1.5987211554602254e-14 -7.1054273576010019e-15 ;
	setAttr ".r" -type "double3" -23.742857290015859 9.5767208242306356 -81.970613393999798 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 23.742857290015838 -9.5767208242306197 81.970613393999784 ;
	setAttr ".ds" 2;
createNode transform -n "rig:SDK1FKThumbFinger3_R" -p "rig:FKOffsetThumbFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003DA";
	setAttr ".ro" 5;
createNode transform -n "rig:FKExtraThumbFinger3_R" -p "rig:SDK1FKThumbFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003DB";
	setAttr -l on -k off ".v";
	setAttr ".ro" 5;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKThumbFinger3_R" -p "rig:FKExtraThumbFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003DC";
	setAttr ".ro" 5;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKThumbFinger3_RShape" -p "rig:FKThumbFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003DD";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-4.2632564149999998e-14 -1.2635222239999999 -1.2635222239999999
		-5.684341886e-14 -2.4158453019999999e-13 -1.7868902659999999
		-5.684341886e-14 1.2635222239999999 -1.2635222239999999
		-5.684341886e-14 1.7868902659999999 1.4921397449999999e-13
		-7.1054273580000001e-14 1.2635222239999999 1.2635222239999999
		-5.684341886e-14 -2.4868995750000001e-13 1.7868902659999999
		-4.2632564149999998e-14 -1.2635222239999999 1.2635222239999999
		-8.5265128290000004e-14 -1.7868902659999999 1.421085472e-13
		-4.2632564149999998e-14 -1.2635222239999999 -1.2635222239999999
		-5.684341886e-14 -2.4158453019999999e-13 -1.7868902659999999
		-5.684341886e-14 1.2635222239999999 -1.2635222239999999
		;
createNode joint -n "rig:FKXThumbFinger3_R" -p "rig:FKThumbFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003DE";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode scaleConstraint -n "rig:FKParentConstraintToWrist_R_scaleConstraint1" 
		-p "rig:FKParentConstraintToWrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003DF";
	addAttr -ci true -k true -sn "w0" -ln "Wrist_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode transform -n "rig:FKParentConstraintToChest_M" -p "rig:FKSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003F2";
	setAttr ".s" -type "double3" 1 0.99999999999999989 1 ;
createNode parentConstraint -n "rig:FKParentConstraintToChest_M_parentConstraint1" 
		-p "rig:FKParentConstraintToChest_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000003F3";
	addAttr -ci true -k true -sn "w0" -ln "Chest_MW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 89.999999999999972 2.8868916598521039 89.999999999999986 ;
	setAttr ".rst" -type "double3" -5.1524607427934986e-14 122.64276660148771 -2.436565956867863 ;
	setAttr ".rsrr" -type "double3" 89.999999999999986 2.8868916598520884 89.999999999999986 ;
	setAttr -k on ".w0";
createNode joint -n "rig:FKOffsetScapula_L" -p "rig:FKParentConstraintToChest_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000041D";
	setAttr ".t" -type "double3" 4.8146220815627601 3.4256949883352354 1.1096741025742134 ;
	setAttr ".r" -type "double3" 85.716654444842078 174.30160351146029 -29.133045817131329 ;
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -87.113108340147875 -89.999999999999972 0 ;
	setAttr ".ds" 2;
createNode transform -n "rig:FKExtraScapula_L" -p "rig:FKOffsetScapula_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000041E";
	setAttr -l on -k off ".v";
	setAttr ".ro" 2;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKScapula_L" -p "rig:FKExtraScapula_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000041F";
	setAttr ".ro" 2;
createNode nurbsCurve -n "rig:FKScapula_LShape" -p "rig:FKScapula_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000420";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		3 18 0 no 3
		23 0 0 0 1 2 3 4 5 6 7 8
		 9 10 11 12 13 14 15 16 17 18 18 18
		
		21
		-15.139322480000001 8.6243209350000001 5.6843418859999999e-13
		-15.139322480000001 8.6243209350000001 -2.2282428780000001
		-14.5047262 6.8441070890000004 -6.870637061
		-12.20664979 0.39738247409999999 -9.6657097660000009
		-9.9085733830000002 -6.0493421410000003 -6.870637061
		-9.2739771050000002 -7.8295559859999999 -2.2282428780000001
		-9.2739771050000002 -7.8295559859999999 5.8264504330000003e-13
		-9.2739771050000002 -7.8295559859999999 5.8264504330000003e-13
		-9.2739771050000002 -7.8295559859999999 5.8264504330000003e-13
		-10.9193648 -8.4160905239999995 5.8264504330000003e-13
		-10.9193648 -8.4160905239999995 5.8264504330000003e-13
		-10.9193648 -8.4160905239999995 5.8264504330000003e-13
		-10.9193648 -8.4160905239999995 -2.2282428780000001
		-11.553961080000001 -6.6358766779999998 -6.870637061
		-13.85203748 -0.18915206330000001 -9.6657097660000009
		-16.15011389 6.2575725520000001 -6.870637061
		-16.78471017 8.0377863969999996 -2.2282428780000001
		-16.78471017 8.0377863969999996 5.9685589799999996e-13
		-16.78471017 8.0377863969999996 5.9685589799999996e-13
		-16.78471017 8.0377863969999996 5.9685589799999996e-13
		-15.139322480000001 8.6243209350000001 5.6843418859999999e-13
		;
createNode joint -n "rig:FKXScapula_L" -p "rig:FKScapula_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000421";
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode transform -n "rig:FKParentConstraintToSpine2_M" -p "rig:FKSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000422";
	setAttr ".s" -type "double3" 1 1 0.99999999999999989 ;
createNode parentConstraint -n "rig:FKParentConstraintToSpine2_M_parentConstraint1" 
		-p "rig:FKParentConstraintToSpine2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000423";
	addAttr -ci true -k true -sn "w0" -ln "Spine2_MW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 89.999999999999972 10.134208501402149 89.999999999999986 ;
	setAttr ".rst" -type "double3" -3.7143271372250579e-14 110.21566086761977 -0.215305426359371 ;
	setAttr ".rsrr" -type "double3" 89.999999999999972 10.134208501402144 89.999999999999972 ;
	setAttr -k on ".w0";
createNode joint -n "rig:FKOffsetBreast_L" -p "rig:FKParentConstraintToSpine2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000429";
	setAttr ".t" -type "double3" 7.1840143228174043 7.9495028875400102 6.6289249529645309 ;
	setAttr ".r" -type "double3" -50.049352591632008 42.141771766787436 118.76944248815805 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -79.865791498597872 -89.999999999999943 0 ;
	setAttr ".ds" 2;
createNode transform -n "rig:FKExtraBreast_L" -p "rig:FKOffsetBreast_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000042A";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKBreast_L" -p "rig:FKExtraBreast_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000042B";
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKBreast_LShape" -p "rig:FKBreast_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000042C";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-11.62363118 3.131915539 3.131915539
		-11.62363118 -2.4576328670000001e-14 4.4291974319999996
		-11.62363118 -3.131915539 3.131915539
		-11.62363118 -4.4291974319999996 5.2142048289999998e-15
		-11.62363118 -3.131915539 -3.131915539
		-11.62363118 -2.842170943e-14 -4.4291974319999996
		-11.62363118 3.131915539 -3.131915539
		-11.62363118 4.4291974319999996 1.0083196239999999e-15
		-11.62363118 3.131915539 3.131915539
		-11.62363118 -2.4576328670000001e-14 4.4291974319999996
		-11.62363118 -3.131915539 3.131915539
		;
createNode joint -n "rig:FKXBreast_L" -p "rig:FKBreast_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000042D";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetRoot_M" -p "rig:FKSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000042E";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode transform -n "rig:FKExtraRoot_M" -p "rig:FKOffsetRoot_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000042F";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
createNode joint -n "rig:FKXRoot_M" -p "rig:FKExtraRoot_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000430";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode orientConstraint -n "rig:FKXRoot_M_orientConstraint1" -p "rig:FKXRoot_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000431";
	addAttr -ci true -k true -sn "w0" -ln "FKRoot_MW0" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "w1" -ln "FKExtraRoot_MW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr ".int" 2;
	setAttr -k on ".w0" 0.33333333333333331;
	setAttr -k on ".w1" 0.66666666666666674;
createNode joint -n "rig:FKOffsetRootPart1_M" -p "rig:FKXRoot_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000432";
	setAttr ".t" -type "double3" 3.3816508661516593 -3.9968028886505635e-15 -3.7860044429179984e-15 ;
	setAttr ".r" -type "double3" 89.999999999999972 -1.7514208112243506 89.999999999999986 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -91.751420811224349 -89.999999999999957 0 ;
	setAttr ".ds" 2;
createNode transform -n "rig:FKExtraRootPart1_M" -p "rig:FKOffsetRootPart1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000433";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKRootPart1_M" -p "rig:FKExtraRootPart1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000434";
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKRootPart1_MShape" -p "rig:FKRootPart1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000435";
	setAttr -l on -k off ".v" no;
	setAttr ".ove" yes;
	setAttr ".ovc" 18;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		0 -11.6349338138522 -11.634933813852181
		0 1.8772700150095521e-15 -16.454281196863086
		0 11.634933813852188 -11.634933813852188
		-6.5937620115942442e-15 16.454281196863086 -5.1286021223093337e-15
		0 11.634933813852191 11.634933813852186
		0 5.5407122480339737e-15 16.454281196863089
		0 -11.634933813852182 11.634933813852189
		6.5937620115942442e-15 -16.454281196863086 8.8375932538310962e-15
		0 -11.6349338138522 -11.634933813852181
		0 1.8772700150095521e-15 -16.454281196863086
		0 11.634933813852188 -11.634933813852188
		;
createNode joint -n "rig:FKXRootPart1_M" -p "rig:FKRootPart1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000436";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode orientConstraint -n "rig:FKXRootPart1_M_orientConstraint1" -p "rig:FKXRootPart1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000437";
	addAttr -ci true -k true -sn "w0" -ln "FKRoot_MW0" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "w1" -ln "FKExtraRoot_MW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr ".int" 2;
	setAttr -k on ".w0" 0.66666666666666663;
	setAttr -k on ".w1" 0.33333333333333337;
createNode joint -n "rig:FKOffsetRootPart2_M" -p "rig:FKXRootPart1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000438";
	setAttr ".t" -type "double3" 3.3816508661518299 2.2204460492503131e-15 -5.6631977693406778e-15 ;
	setAttr ".r" -type "double3" 89.999999999999972 -1.7514208112243506 89.999999999999986 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -91.751420811224349 -89.999999999999957 0 ;
	setAttr ".ds" 2;
createNode transform -n "rig:FKExtraRootPart2_M" -p "rig:FKOffsetRootPart2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000439";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKRootPart2_M" -p "rig:FKExtraRootPart2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000043A";
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKRootPart2_MShape" -p "rig:FKRootPart2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000043B";
	setAttr -l on -k off ".v" no;
	setAttr ".ove" yes;
	setAttr ".ovc" 18;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		0 -11.6349338138522 -11.634933813852181
		0 1.8772700150095521e-15 -16.454281196863086
		0 11.634933813852188 -11.634933813852188
		-6.5937620115942442e-15 16.454281196863086 -5.1286021223093337e-15
		0 11.634933813852191 11.634933813852186
		0 5.5407122480339737e-15 16.454281196863089
		0 -11.634933813852182 11.634933813852189
		6.5937620115942442e-15 -16.454281196863086 8.8375932538310962e-15
		0 -11.6349338138522 -11.634933813852181
		0 1.8772700150095521e-15 -16.454281196863086
		0 11.634933813852188 -11.634933813852188
		;
createNode joint -n "rig:FKXRootPart2_M" -p "rig:FKRootPart2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000043C";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode orientConstraint -n "rig:FKXRootPart2_M_orientConstraint1" -p "rig:FKXRootPart2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000043D";
	addAttr -ci true -k true -sn "w0" -ln "FKRoot_MW0" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "w1" -ln "FKExtraRoot_MW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr ".int" 2;
	setAttr -k on ".w0";
	setAttr -k on ".w1" 0;
createNode joint -n "rig:FKOffsetSpine1_M" -p "rig:FKXRootPart2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000043E";
	setAttr ".t" -type "double3" 3.3816508661515599 -3.5527136788005009e-15 -1.5112399981599095e-14 ;
	setAttr ".r" -type "double3" 89.999999999999972 5.0918278134747608 89.999999999999986 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -91.751420811224349 -89.999999999999957 0 ;
	setAttr ".ds" 2;
createNode transform -n "rig:FKExtraSpine1_M" -p "rig:FKOffsetSpine1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000043F";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKSpine1_M" -p "rig:FKExtraSpine1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000440";
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKSpine1_MShape" -p "rig:FKSpine1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000441";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 18;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		0 -11.63493381 -11.63493381
		0 1.8772700149999998e-15 -16.4542812
		0 11.63493381 -11.63493381
		-6.5937620120000003e-15 16.4542812 -5.128602122e-15
		0 11.63493381 11.63493381
		0 5.5407122479999998e-15 16.4542812
		0 -11.63493381 11.63493381
		6.5937620120000003e-15 -16.4542812 8.8375932540000008e-15
		0 -11.63493381 -11.63493381
		0 1.8772700149999998e-15 -16.4542812
		0 11.63493381 -11.63493381
		;
createNode joint -n "rig:FKXSpine1_M" -p "rig:FKSpine1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000442";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetSpine2_M" -p "rig:FKXSpine1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000443";
	setAttr ".t" -type "double3" 11.252214457917404 -1.7763568394002505e-15 -2.0224679794353742e-14 ;
	setAttr ".r" -type "double3" 89.999999999999972 10.13420850140214 89.999999999999972 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -84.908172186525235 -89.999999999999972 0 ;
	setAttr ".ds" 2;
createNode transform -n "rig:FKExtraSpine2_M" -p "rig:FKOffsetSpine2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000444";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKSpine2_M" -p "rig:FKExtraSpine2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000445";
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKSpine2_MShape" -p "rig:FKSpine2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000446";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 18;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		0 -11.63493381 -11.63493381
		0 1.8772700149999998e-15 -16.4542812
		-5.231835341 10.02420639 -11.63493381
		-5.231835341 14.84355377 -5.128602122e-15
		-5.231835341 10.02420639 11.63493381
		0 5.5407122479999998e-15 16.4542812
		0 -11.63493381 11.63493381
		6.5937620120000003e-15 -16.4542812 8.8375932540000008e-15
		0 -11.63493381 -11.63493381
		0 1.8772700149999998e-15 -16.4542812
		-5.231835341 10.02420639 -11.63493381
		;
createNode joint -n "rig:FKXSpine2_M" -p "rig:FKSpine2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000447";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetChest_M" -p "rig:FKXSpine2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000448";
	setAttr ".t" -type "double3" 12.624062549953081 7.1054273576010019e-15 -1.998754601859085e-14 ;
	setAttr ".r" -type "double3" 89.999999999999972 2.8868916598520808 89.999999999999972 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -79.865791498597872 -89.999999999999943 0 ;
	setAttr ".ds" 2;
createNode transform -n "rig:FKExtraChest_M" -p "rig:FKOffsetChest_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000449";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKChest_M" -p "rig:FKExtraChest_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000044A";
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKChest_MShape" -p "rig:FKChest_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000044B";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 18;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		0 -11.63493381 -11.63493381
		0 1.8772700149999998e-15 -16.4542812
		0 11.63493381 -11.63493381
		-6.5937620120000003e-15 16.4542812 -5.128602122e-15
		0 11.63493381 11.63493381
		0 5.5407122479999998e-15 16.4542812
		0 -11.63493381 11.63493381
		6.5937620120000003e-15 -16.4542812 8.8375932540000008e-15
		0 -11.63493381 -11.63493381
		0 1.8772700149999998e-15 -16.4542812
		0 11.63493381 -11.63493381
		;
createNode joint -n "rig:FKXChest_M" -p "rig:FKChest_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000044C";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode transform -n "rig:AlignIKToChest_M" -p "rig:FKXChest_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000044D";
	setAttr ".r" -type "double3" -87.113108340147932 -89.999999999999957 0 ;
createNode transform -n "rig:HipSwingerStabilizer" -p "rig:FKExtraRoot_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000044E";
	setAttr ".s" -type "double3" 1 1.0000000000000002 1.0000000000000002 ;
createNode transform -n "rig:FKRoot_M" -p "rig:HipSwingerStabilizer";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000044F";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKRoot_MShape" -p "rig:FKRoot_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000450";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 18;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		0 -11.63493381 -11.63493381
		0 1.8772700149999998e-15 -16.4542812
		0 11.63493381 -11.63493381
		-6.5937620120000003e-15 16.4542812 -5.128602122e-15
		0 11.63493381 11.63493381
		0 5.5407122479999998e-15 16.4542812
		0 -11.63493381 11.63493381
		6.5937620120000003e-15 -16.4542812 8.8375932540000008e-15
		0 -11.63493381 -11.63493381
		0 1.8772700149999998e-15 -16.4542812
		0 11.63493381 -11.63493381
		;
createNode orientConstraint -n "rig:HipSwingerStabilizer_orientConstraint1" -p "rig:HipSwingerStabilizer";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000451";
	addAttr -ci true -k true -sn "w0" -ln "HipSwingerStabilizerTargetW0" -dv 1 -min 
		0 -at "double";
	addAttr -ci true -k true -sn "w1" -ln "HipSwingerStabilizerTarget2W1" -dv 1 -min 
		0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr -k on ".w0";
	setAttr -k on ".w1";
createNode transform -n "rig:HipSwingerStabilizerTarget2" -p "rig:FKExtraRoot_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000452";
	setAttr ".t" -type "double3" 5.07247629922756 1.9095836023552692e-14 -21.319963996789635 ;
	setAttr ".r" -type "double3" 5.6498000615042016e-30 4.4139062980501602e-30 0 ;
	setAttr ".s" -type "double3" 0.99999999999999989 1.0000000000000002 1 ;
createNode parentConstraint -n "rig:FKOffsetRoot_M_parentConstraint1" -p "rig:FKOffsetRoot_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000453";
	addAttr -ci true -k true -sn "w0" -ln "HipSwingReverseSpine1W0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 89.999999999999972 -1.751420811224351 90 ;
	setAttr ".rst" -type "double3" -5.8064397712757788e-15 88.867637422588331 0.47329046439253208 ;
	setAttr ".rsrr" -type "double3" 89.999999999999972 -1.7514208112243506 89.999999999999986 ;
	setAttr -k on ".w0";
createNode transform -n "rig:FKParentConstraintToScapula_L" -p "rig:FKSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004CB";
	setAttr ".s" -type "double3" 1.0000000000000004 1.0000000000000002 1.0000000000000004 ;
createNode parentConstraint -n "rig:FKParentConstraintToScapula_L_parentConstraint1" 
		-p "rig:FKParentConstraintToScapula_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004CC";
	addAttr -ci true -k true -sn "w0" -ln "Scapula_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 85.356850077671282 203.35018097290126 2.2698015910308365 ;
	setAttr ".rst" -type "double3" 1.1096741025741619 127.62381171178188 0.74229571841643605 ;
	setAttr ".rsrr" -type "double3" 85.356850077671311 203.35018097290126 2.2698015910307854 ;
	setAttr -k on ".w0";
createNode joint -n "rig:FKOffsetShoulder_L" -p "rig:FKParentConstraintToScapula_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004CD";
	setAttr ".t" -type "double3" -14.409854929115941 -8.8817841970012523e-15 -4.4053649617126212e-13 ;
	setAttr ".r" -type "double3" 137.37377870439639 -76.771686676703098 -136.18742614256152 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -94.262256953728155 -0.42490937423914937 -156.54953871368423 ;
	setAttr ".ds" 2;
createNode transform -n "rig:FKExtraShoulder_L" -p "rig:FKOffsetShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004CE";
	setAttr -l on -k off ".v";
	setAttr ".ro" 5;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKShoulder_L" -p "rig:FKExtraShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004CF";
	setAttr ".ro" 5;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKShoulder_LShape" -p "rig:FKShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004D0";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-1.4210854720000001e-14 6.8440787140000001 6.8440787140000001
		0 0 9.6789889389999999
		0 -6.8440787140000001 6.8440787140000001
		-1.4210854720000001e-14 -9.6789889389999999 7.1054273579999998e-15
		-1.4210854720000001e-14 -6.8440787140000001 -6.8440787140000001
		0 -3.5527136789999999e-15 -9.6789889389999999
		-1.4210854720000001e-14 6.8440787140000001 -6.8440787140000001
		-1.4210854720000001e-14 9.6789889389999999 -7.1054273579999998e-15
		-1.4210854720000001e-14 6.8440787140000001 6.8440787140000001
		0 0 9.6789889389999999
		0 -6.8440787140000001 6.8440787140000001
		;
createNode joint -n "rig:FKXShoulder_L" -p "rig:FKShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004D1";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetElbow_L" -p "rig:FKXShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004D2";
	setAttr ".t" -type "double3" -28.609776476120302 3.1974423109204508e-14 3.5527136788005009e-14 ;
	setAttr ".r" -type "double3" 137.37377870439644 -76.771686676703098 -111.8028902357388 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -137.37377870439644 76.771686676703183 136.18742614256146 ;
	setAttr ".ds" 2;
createNode transform -n "rig:FKExtraElbow_L" -p "rig:FKOffsetElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004D3";
	setAttr -l on -k off ".v";
	setAttr ".ro" 5;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKElbow_L" -p "rig:FKExtraElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004D4";
	setAttr ".ro" 5;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKElbow_LShape" -p "rig:FKElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004D5";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		2.842170943e-14 4.7382083399999999 4.7382083399999999
		2.842170943e-14 0 6.7008384960000003
		2.842170943e-14 -4.7382083399999999 4.7382083399999999
		4.2632564149999998e-14 -6.7008384960000003 -1.4210854720000001e-14
		4.2632564149999998e-14 -4.7382083399999999 -4.7382083399999999
		2.842170943e-14 -3.5527136789999999e-15 -6.7008384960000003
		2.842170943e-14 4.7382083399999999 -4.7382083399999999
		4.2632564149999998e-14 6.7008384960000003 -7.1054273579999998e-15
		2.842170943e-14 4.7382083399999999 4.7382083399999999
		2.842170943e-14 0 6.7008384960000003
		2.842170943e-14 -4.7382083399999999 4.7382083399999999
		;
createNode joint -n "rig:FKXElbow_L" -p "rig:FKElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004D6";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:FKOffsetWrist_L" -p "rig:FKXElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004D7";
	setAttr ".t" -type "double3" -22.761072191110145 -8.8817841970012523e-14 -2.5579538487363607e-13 ;
	setAttr ".r" -type "double3" 128.26616798566252 -81.235819171498065 -109.20479172099709 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -137.3737787043965 76.771686676703098 111.80289023573867 ;
	setAttr ".ds" 2;
createNode transform -n "rig:FKExtraWrist_L" -p "rig:FKOffsetWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004D8";
	setAttr -l on -k off ".v";
	setAttr ".ro" 5;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:FKWrist_L" -p "rig:FKExtraWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004D9";
	setAttr ".ro" 5;
	setAttr ".smd" 2;
createNode nurbsCurve -n "rig:FKWrist_LShape" -p "rig:FKWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004DA";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-1.4210854720000001e-14 4.1348764779999998 4.1348764779999998
		-2.842170943e-14 7.1054273579999998e-15 5.8475983950000003
		-5.684341886e-14 -4.1348764779999998 4.1348764779999998
		-2.842170943e-14 -5.8475983950000003 7.1054273579999998e-15
		-1.4210854720000001e-14 -4.1348764779999998 -4.1348764779999998
		-1.4210854720000001e-14 0 -5.8475983950000003
		0 4.1348764779999998 -4.1348764779999998
		-2.842170943e-14 5.8475983950000003 7.1054273579999998e-15
		-1.4210854720000001e-14 4.1348764779999998 4.1348764779999998
		-2.842170943e-14 7.1054273579999998e-15 5.8475983950000003
		-5.684341886e-14 -4.1348764779999998 4.1348764779999998
		;
createNode joint -n "rig:FKXWrist_L" -p "rig:FKWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004DB";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode transform -n "rig:AlignIKToWrist_L" -p "rig:FKXWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004DC";
	setAttr ".r" -type "double3" 96.437812315763082 -32.690834179111675 -93.414234120871825 ;
	setAttr ".ro" 5;
	setAttr ".s" -type "double3" 1 1.0000000000000002 1 ;
createNode transform -n "bundle1_BND" -p "rig:FKShoulder_L";
	rename -uid "24566900-0000-06C4-5D33-A89A000012C8";
	setAttr ".t" -type "double3" -22.260731264129497 -5.1856410178197327 -2.8421709430404052e-14 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -l on ".shxy";
	setAttr -l on ".shxz";
	setAttr -l on ".shyz";
createNode locator -n "bundle1_BNDShape" -p "bundle1_BND";
	rename -uid "24566900-0000-06C4-5D33-A89A000012C9";
	setAttr -k off ".v";
	setAttr ".wfcc" -type "float3" 0 1 0 ;
	setAttr ".uoc" 2;
	setAttr ".los" -type "double3" 9.6 9.6 9.6 ;
createNode transform -n "rig:HipSwingerOffset_M" -p "rig:FKSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004DD";
	setAttr ".t" -type "double3" -21.319963996789642 93.937744029500095 0.62832207657223249 ;
	setAttr ".r" -type "double3" 89.999999999999972 -1.7514208112243506 89.999999999999986 ;
	setAttr ".s" -type "double3" 0.99999999999999978 1 1.0000000000000002 ;
createNode transform -n "rig:HipSwinger_M" -p "rig:HipSwingerOffset_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004DE";
	addAttr -ci true -k true -sn "stabilize" -ln "stabilize" -dv 10 -min 0 -max 10 
		-at "double";
	setAttr ".t" -type "double3" 0 0 -1.2621774483536189e-29 ;
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr ".s" -type "double3" 1.0000000000000002 1.0000000000000002 1 ;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -k on ".stabilize";
createNode nurbsCurve -n "rig:HipSwinger_MShape" -p "rig:HipSwinger_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004DF";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 22;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8
		 9 10
		11
		-9.3079470509999993 -5.6994737810000001e-16 9.3079470509999993
		-1.8772367399999999e-15 1.0075341400000001e-15 -16.4542812
		9.3079470509999993 -5.6994737810000001e-16 9.3079470509999993
		-16.4542812 2.9195818730000001e-31 -4.7680390370000001e-15
		9.3079470509999993 5.6994737810000001e-16 -9.3079470509999993
		-4.9579960479999998e-15 -1.0075341400000001e-15 16.4542812
		-9.3079470509999993 5.6994737810000001e-16 -9.3079470509999993
		16.4542812 -5.4114855199999998e-31 8.8376265290000003e-15
		-9.3079470509999993 -5.6994737810000001e-16 9.3079470509999993
		-1.8772367399999999e-15 1.0075341400000001e-15 -16.4542812
		9.3079470509999993 -5.6994737810000001e-16 9.3079470509999993
		;
createNode transform -n "rig:HipSwingerStabilizerTarget" -p "rig:HipSwingerOffset_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004E0";
	setAttr ".t" -type "double3" 0 -4.4408920985006262e-16 3.5527136788005009e-15 ;
	setAttr ".r" -type "double3" 1.1299600123008406e-29 1.9421187711420696e-30 0 ;
	setAttr ".s" -type "double3" 1 1 0.99999999999999989 ;
createNode transform -n "rig:HipSwingReverseNeg" -p "rig:FKSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004E1";
	setAttr ".t" -type "double3" -2.5048665071004583e-14 99.00785063641176 0.78335368875192013 ;
	setAttr ".r" -type "double3" 89.999999999999972 -1.7514208112243512 89.999999999999986 ;
	setAttr ".s" -type "double3" -1 0.99999999999999978 1.0000000000000002 ;
createNode transform -n "rig:HipSwingReversePart1" -p "rig:HipSwingReverseNeg";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004E2";
	setAttr ".t" -type "double3" 3.3816508661516451 -4.8849813083506888e-15 -3.7860044429180111e-15 ;
	setAttr ".s" -type "double3" 1.0000000000000002 1.0000000000000004 1 ;
createNode transform -n "rig:HipSwingReversePart2" -p "rig:HipSwingReversePart1";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004E3";
	setAttr ".t" -type "double3" 3.3816508661518725 3.5527136788005009e-15 -7.5403910957633634e-15 ;
	setAttr ".s" -type "double3" 1.0000000000000002 1.0000000000000002 1 ;
createNode transform -n "rig:HipSwingReverseSpine1" -p "rig:HipSwingReversePart2";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004E4";
	setAttr ".t" -type "double3" 3.3816508661515172 -3.5527136788005009e-15 -1.8866786634444126e-14 ;
createNode orientConstraint -n "rig:HipSwingReverseSpine1_orientConstraint1" -p "rig:HipSwingReverseSpine1";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004E5";
	addAttr -ci true -k true -sn "w0" -ln "HipSwinger_MW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:HipSwingReversePart2_orientConstraint1" -p "rig:HipSwingReversePart2";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004E6";
	addAttr -ci true -k true -sn "w0" -ln "HipSwingerStabilizerTargetW0" -dv 1 -min 
		0 -at "double";
	addAttr -ci true -k true -sn "w1" -ln "HipSwinger_MW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr -k on ".w0" 0.33333333333333337;
	setAttr -k on ".w1" 0.66666666666666663;
createNode orientConstraint -n "rig:HipSwingReversePart1_orientConstraint1" -p "rig:HipSwingReversePart1";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000004E7";
	addAttr -ci true -k true -sn "w0" -ln "HipSwingerStabilizerTargetW0" -dv 1 -min 
		0 -at "double";
	addAttr -ci true -k true -sn "w1" -ln "HipSwinger_MW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr ".lr" -type "double3" -180 0 0 ;
	setAttr -k on ".w0" 0.66666666666666674;
	setAttr -k on ".w1" 0.33333333333333331;
createNode transform -n "rig:FKIKSystem" -p "rig:MotionSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000610";
createNode transform -n "rig:FKIKParentConstraintSpine_M" -p "rig:FKIKSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000619";
createNode parentConstraint -n "rig:FKIKParentConstraintSpine_M_parentConstraint1" 
		-p "rig:FKIKParentConstraintSpine_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000061A";
	addAttr -ci true -k true -sn "w0" -ln "Root_MW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 89.999999999999972 -1.751420811224351 90 ;
	setAttr ".rst" -type "double3" 1.7655691145602508e-15 88.867637422588331 0.47329046439254197 ;
	setAttr ".rsrr" -type "double3" 89.999999999999972 -1.7514208112243506 89.999999999999986 ;
	setAttr -k on ".w0";
createNode transform -n "rig:FKIKSpine_M" -p "rig:FKIKParentConstraintSpine_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000061B";
	addAttr -ci true -k true -sn "FKIKBlend" -ln "FKIKBlend" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "autoVis" -ln "autoVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "FKVis" -ln "FKVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "IKVis" -ln "IKVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "startJoint" -ln "startJoint" -dt "string";
	addAttr -ci true -sn "middleJoint" -ln "middleJoint" -dt "string";
	addAttr -ci true -sn "endJoint" -ln "endJoint" -dt "string";
	setAttr -l on -k off ".v";
	setAttr ".t" -type "double3" 10.061305999755859 -4.4408920985006262e-16 17.240806901977063 ;
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr ".r" -type "double3" -91.751420811224349 -89.999999999999957 0 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr ".s" -type "double3" 1 1.0000000000000002 1.0000000000000002 ;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -k on ".FKIKBlend";
	setAttr -cb on ".autoVis";
	setAttr -k on ".FKVis";
	setAttr -k on ".IKVis";
	setAttr -l on ".startJoint" -type "string" "Root";
	setAttr -l on ".middleJoint" -type "string" "RootPart2";
	setAttr -l on ".endJoint" -type "string" "Chest";
createNode nurbsCurve -n "rig:FKIKSpine_MShape" -p "rig:FKIKSpine_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000061C";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		1 12 2 no 3
		13 0 1 2 3 4 5 6 7 8 9 10
		 11 12
		13
		-2.0122611899999998 0.28744286689999998 -3.8298660310000002e-16
		-0.28744286689999998 0.28744286689999998 0
		-0.28744286689999998 2.0122611899999998 3.8302237940000001e-16
		0.28744286689999998 2.0122611899999998 5.1067265499999999e-16
		0.28744286689999998 0.28744286689999998 1.276502756e-16
		2.0122611899999998 0.28744286689999998 5.1063687870000004e-16
		2.0122611899999998 -0.28744286689999998 3.8298660310000002e-16
		0.28744286689999998 -0.28744286689999998 0
		0.28744286689999998 -2.0122611899999998 -3.8302237940000001e-16
		-0.28744286689999998 -2.0122611899999998 -5.1067265499999999e-16
		-0.28744286689999998 -0.28744286689999998 -1.276502756e-16
		-2.0122611899999998 -0.28744286689999998 -5.1063687870000004e-16
		-2.0122611899999998 0.28744286689999998 -3.8298660310000002e-16
		;
createNode transform -n "rig:FKIKParentConstraintArm_L" -p "rig:FKIKSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000621";
createNode parentConstraint -n "rig:FKIKParentConstraintArm_L_parentConstraint1" 
		-p "rig:FKIKParentConstraintArm_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000622";
	addAttr -ci true -k true -sn "w0" -ln "Scapula_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 85.356850077671282 203.35018097290126 2.2698015910308365 ;
	setAttr ".rst" -type "double3" 1.1096741025741261 127.62381171178185 0.74229571841644049 ;
	setAttr ".rsrr" -type "double3" 85.356850077671311 203.35018097290126 2.2698015910307854 ;
	setAttr -k on ".w0";
createNode transform -n "rig:FKIKArm_L" -p "rig:FKIKParentConstraintArm_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000623";
	addAttr -ci true -k true -sn "FKIKBlend" -ln "FKIKBlend" -min 0 -max 10 -at "double";
	addAttr -ci true -sn "autoVis" -ln "autoVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "FKVis" -ln "FKVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "IKVis" -ln "IKVis" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "startJoint" -ln "startJoint" -dt "string";
	addAttr -ci true -sn "middleJoint" -ln "middleJoint" -dt "string";
	addAttr -ci true -sn "endJoint" -ln "endJoint" -dt "string";
	setAttr -l on -k off ".v";
	setAttr ".t" -type "double3" -22.283296024645914 -5.0286862751558346 8.6797125336960335 ;
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr ".r" -type "double3" -94.262256953728169 -0.42490937423915393 -156.5495387136842 ;
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr ".s" -type "double3" 1.0000000000000002 1 1 ;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -k on ".FKIKBlend";
	setAttr -cb on ".autoVis";
	setAttr -k on ".FKVis";
	setAttr -k on ".IKVis";
	setAttr -l on ".startJoint" -type "string" "Shoulder";
	setAttr -l on ".middleJoint" -type "string" "Elbow";
	setAttr -l on ".endJoint" -type "string" "Wrist";
createNode nurbsCurve -n "rig:FKIKArm_LShape" -p "rig:FKIKArm_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000624";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		1 12 2 no 3
		13 0 1 2 3 4 5 6 7 8 9 10
		 11 12
		13
		-2.0122611899999998 0.28744286689999998 -8.881784197e-16
		-0.28744286689999998 0.28744286689999998 -4.4408920989999998e-16
		-0.28744286689999998 2.0122611899999998 0
		0.28744286689999998 2.0122611899999998 4.4408920989999998e-16
		0.28744286689999998 0.28744286689999998 0
		2.0122611899999998 0.28744286689999998 0
		2.0122611899999998 -0.28744286689999998 0
		0.28744286689999998 -0.28744286689999998 0
		0.28744286689999998 -2.0122611899999998 -4.4408920989999998e-16
		-0.28744286689999998 -2.0122611899999998 -8.881784197e-16
		-0.28744286689999998 -0.28744286689999998 -4.4408920989999998e-16
		-2.0122611899999998 -0.28744286689999998 -4.4408920989999998e-16
		-2.0122611899999998 0.28744286689999998 -8.881784197e-16
		;
createNode transform -n "rig:RootSystem" -p "rig:MotionSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000627";
createNode transform -n "rig:LegLockConstrained" -p "rig:RootSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000628";
createNode pointConstraint -n "rig:LegLockConstrained_pointConstraint1" -p "rig:LegLockConstrained";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000629";
	addAttr -ci true -k true -sn "w0" -ln "Root_MW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 1.7655691145602508e-15 88.867637422588331 0.47329046439254197 ;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:LegLockConstrained_orientConstraint1" -p "rig:LegLockConstrained";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000062A";
	addAttr -ci true -k true -sn "w0" -ln "RootX_MW0" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "w1" -ln "RootSpineAlignedW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr -k on ".w0";
	setAttr -k on ".w1";
createNode transform -n "rig:RootCenterBtwLegsBlended_M" -p "rig:RootSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000062B";
createNode transform -n "rig:RootOffsetX_M" -p "rig:RootCenterBtwLegsBlended_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000062C";
	setAttr ".t" -type "double3" 7.57200888583603e-15 0 9.8809849191638932e-15 ;
createNode transform -n "rig:RootExtraX_M" -p "rig:RootOffsetX_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000062D";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode transform -n "rig:RootX_M" -p "rig:RootExtraX_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000062E";
	addAttr -ci true -k true -sn "legLock" -ln "legLock" -min 0 -max 10 -at "double";
	addAttr -ci true -k true -sn "CenterBtwFeet" -ln "CenterBtwFeet" -min 0 -max 10 
		-at "double";
	setAttr ".ro" 3;
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr -k on ".legLock";
	setAttr -k on ".CenterBtwFeet";
createNode nurbsCurve -n "rig:curveShape1" -p "rig:RootX_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000062F";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 15;
	setAttr ".cc" -type "nurbsCurve" 
		1 7 2 no 3
		8 0 1 2 3 4 5 6 7
		8
		-16.79588893 0 -1.6315078590000001
		-19.16166711 0 -1.6315078590000001
		-19.16166711 0 -4.5530450729999998
		-23.714712179999999 0 0
		-19.16166711 0 4.5530450729999998
		-19.16166711 0 1.6315078590000001
		-16.79588893 0 1.6315078590000001
		-16.79588893 0 -1.6315078590000001
		;
createNode nurbsCurve -n "rig:curveShape2" -p "rig:RootX_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000630";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 15;
	setAttr ".cc" -type "nurbsCurve" 
		1 7 2 no 3
		8 0 1 2 3 4 5 6 7
		8
		-1.6315078590000001 0 16.79588893
		-1.6315078590000001 0 19.16166711
		-4.5530450729999998 0 19.16166711
		-5.2657238969999998e-15 0 23.714712179999999
		4.5530450729999998 0 19.16166711
		1.6315078590000001 0 19.16166711
		1.6315078590000001 0 16.79588893
		-1.6315078590000001 0 16.79588893
		;
createNode nurbsCurve -n "rig:curveShape3" -p "rig:RootX_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000631";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 15;
	setAttr ".cc" -type "nurbsCurve" 
		1 7 2 no 3
		8 0 1 2 3 4 5 6 7
		8
		16.79588893 0 1.6315078590000001
		19.16166711 0 1.6315078590000001
		19.16166711 0 4.5530450729999998
		23.714712179999999 0 1.053144779e-14
		19.16166711 0 -4.5530450729999998
		19.16166711 0 -1.6315078590000001
		16.79588893 0 -1.6315078590000001
		16.79588893 0 1.6315078590000001
		;
createNode nurbsCurve -n "rig:curveShape4" -p "rig:RootX_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000632";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 15;
	setAttr ".cc" -type "nurbsCurve" 
		1 7 2 no 3
		8 0 1 2 3 4 5 6 7
		8
		1.6315078590000001 0 -16.79588893
		1.6315078590000001 0 -19.16166711
		4.5530450729999998 0 -19.16166711
		1.5797171689999999e-14 0 -23.714712179999999
		-4.5530450729999998 0 -19.16166711
		-1.6315078590000001 0 -19.16166711
		-1.6315078590000001 0 -16.79588893
		1.6315078590000001 0 -16.79588893
		;
createNode transform -n "rig:RootZeroXform" -p "rig:RootX_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000633";
	setAttr ".t" -type "double3" -1.7655691145602508e-15 -88.867637422588331 -0.47329046439254197 ;
createNode transform -n "rig:RootSpineAligned" -p "rig:RootX_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000634";
createNode orientConstraint -n "rig:RootSpineAligned_orientConstraint1" -p "rig:RootSpineAligned";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000635";
	addAttr -ci true -k true -sn "w0" -ln "Root_MW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 89.999999999999972 -1.751420811224351 90 ;
	setAttr ".o" -type "double3" -91.751420811224349 -89.999999999999972 0 ;
	setAttr ".rsrr" -type "double3" 3.180554681463514e-15 -3.1805546814635168e-14 9.5416640443905487e-15 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:RootCenterBtwLegsBlended_M_parentConstraint1" 
		-p "rig:RootCenterBtwLegsBlended_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000636";
	addAttr -ci true -k true -sn "w0" -ln "RootCenter_MW0" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "w1" -ln "RootCenterBtwLegsOffset_MW1" -dv 1 -min 0 
		-at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr ".rst" -type "double3" -5.8064397712757772e-15 88.867637422588331 0.47329046439253203 ;
	setAttr -k on ".w0";
	setAttr -k on ".w1";
createNode transform -n "rig:RootCenter_M" -p "rig:RootSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000637";
	setAttr ".t" -type "double3" -5.8064397712757788e-15 88.867637422588331 0.47329046439253208 ;
	setAttr ".r" -type "double3" 3.1805546814634903e-15 -3.3166462247508187e-14 2.8604190241232386e-14 ;
createNode transform -n "rig:RootCenterBtwLegs_M" -p "rig:RootSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000638";
	setAttr ".t" -type "double3" 3.9968028886505635e-14 88.867637422588331 -5.6101808417093189 ;
	setAttr ".r" -type "double3" 3.1805546814634903e-15 0 2.8604190241232386e-14 ;
createNode transform -n "rig:RootCenterBtwLegsOffset_M" -p "rig:RootCenterBtwLegs_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000063B";
	setAttr ".t" -type "double3" -4.5774468657781411e-14 0 6.0834713061018508 ;
createNode transform -n "rig:TwistSystem" -p "rig:MotionSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000063C";
createNode transform -n "rig:TwistFollowOffsetNeck1_M" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000063D";
	setAttr ".t" -type "double3" -9.4677208292113494e-14 136.51647378548182 -1.8640316638796552 ;
	setAttr ".r" -type "double3" 89.999999999999858 -17.009868441056724 90.000000000000128 ;
	setAttr ".s" -type "double3" 0.99999999999999989 1 1.0000000000000002 ;
createNode transform -n "rig:TwistFollowNeck1_M" -p "rig:TwistFollowOffsetNeck1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000063E";
	setAttr -l on ".v" no;
	setAttr ".t" -type "double3" -9.4677208292113494e-14 136.51647378548182 -1.8640316638796552 ;
	setAttr ".r" -type "double3" 89.999999999999858 -17.009868441056724 90.000000000000128 ;
	setAttr ".s" -type "double3" 0.99999999999999989 1 1 ;
createNode ikHandle -n "rig:UnTwistIKNeck1_M" -p "rig:TwistFollowNeck1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000640";
	setAttr ".t" -type "double3" 1 -7.1054273576010019e-15 1.5543122344752318e-15 ;
	setAttr ".r" -type "double3" -107.00986844105671 -89.999999999999844 0 ;
	setAttr ".s" -type "double3" 0.99999999999999967 1 0.99999999999999978 ;
	setAttr ".roc" yes;
createNode poleVectorConstraint -n "rig:UnTwistIKNeck1_M_poleVectorConstraint1" -p
		 "rig:UnTwistIKNeck1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000641";
	addAttr -ci true -k true -sn "w0" -ln "UnTwistNeck1_MW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode transform -n "rig:TwistFollowParentOffsetNeck1_M" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000642";
	setAttr ".t" -type "double3" -6.4866180093951288e-14 132.94646449187445 -2.9561654346275312 ;
	setAttr ".r" -type "double3" 89.999999999999957 -17.009868441056721 90.000000000000028 ;
	setAttr ".s" -type "double3" 1 1 1.0000000000000002 ;
createNode transform -n "rig:TwistFollowParentNeck1_M" -p "rig:TwistFollowParentOffsetNeck1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000643";
	setAttr -l on ".v" no;
	setAttr ".t" -type "double3" -6.4866180093951288e-14 132.94646449187445 -2.9561654346275312 ;
	setAttr ".r" -type "double3" 89.999999999999957 -17.009868441056721 90.000000000000028 ;
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999989 0.99999999999999978 ;
createNode joint -n "rig:UnTwistNeck1_M" -p "rig:TwistFollowParentNeck1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000645";
	setAttr ".t" -type "double3" 3.7333259340232985 -1.4210854715202004e-14 -2.8153098434009046e-14 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:UnTwistEndNeck1_M" -p "rig:UnTwistNeck1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000646";
	setAttr ".t" -type "double3" 1 0 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode ikEffector -n "rig:effector1" -p "rig:UnTwistNeck1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000648";
	setAttr ".v" no;
	setAttr ".hd" yes;
createNode joint -n "rig:TwistBalancerNeck1_M" -p "rig:UnTwistNeck1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000649";
	setAttr ".t" -type "double3" 0 7.1054273576010019e-15 -1.2621774483536189e-29 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode transform -n "rig:TwistFollowOffsetChest_M" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000064B";
	setAttr ".t" -type "double3" -4.7347378888852619e-15 122.64276577588309 -2.4365658857388732 ;
	setAttr ".r" -type "double3" 89.999999999999957 4.924091341079869 89.999999999999972 ;
	setAttr ".s" -type "double3" 0.99999999999999967 0.99999999999999978 1 ;
createNode transform -n "rig:TwistFollowChest_M" -p "rig:TwistFollowOffsetChest_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000064C";
	setAttr -l on ".v" no;
	setAttr ".t" -type "double3" -4.7347378888852619e-15 122.64276577588309 -2.4365658857388732 ;
	setAttr ".r" -type "double3" 89.999999999999957 4.9240913410798681 89.999999999999972 ;
	setAttr ".s" -type "double3" 1.0000000000000002 1.0000000000000002 1 ;
createNode ikHandle -n "rig:UnTwistIKChest_M" -p "rig:TwistFollowChest_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000064E";
	setAttr ".t" -type "double3" 0.99936795764214992 0.03554835070958795 -3.0560084871176845e-15 ;
	setAttr ".r" -type "double3" -85.075908658920142 -89.999999999999957 0 ;
	setAttr ".s" -type "double3" 1 1.0000000000000002 1 ;
	setAttr ".roc" yes;
createNode poleVectorConstraint -n "rig:UnTwistIKChest_M_poleVectorConstraint1" -p
		 "rig:UnTwistIKChest_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000064F";
	addAttr -ci true -k true -sn "w0" -ln "UnTwistChest_MW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode transform -n "rig:TwistFollowParentOffsetChest_M" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000650";
	setAttr ".t" -type "double3" 1.765569114560251e-15 88.867637422588331 0.47329046439254152 ;
	setAttr ".r" -type "double3" 89.999999999999986 -1.7514208112243443 90.000000000000142 ;
createNode transform -n "rig:TwistFollowParentChest_M" -p "rig:TwistFollowParentOffsetChest_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000651";
	setAttr -l on ".v" no;
	setAttr ".t" -type "double3" 1.765569114560251e-15 88.867637422588331 0.47329046439254152 ;
	setAttr ".r" -type "double3" 89.999999999999986 -1.7514208112243503 90.000000000000142 ;
	setAttr ".s" -type "double3" 0.99999999999999989 1 0.99999999999999978 ;
createNode joint -n "rig:UnTwistChest_M" -p "rig:TwistFollowParentChest_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000653";
	setAttr ".t" -type "double3" 33.670414924988137 -3.9407763244151082 8.2340672630672267e-14 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 -4.6383124710764223 ;
	setAttr ".ds" 2;
createNode joint -n "rig:UnTwistEndChest_M" -p "rig:UnTwistChest_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000654";
	setAttr ".t" -type "double3" 1 0 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode ikEffector -n "rig:effector2" -p "rig:UnTwistChest_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000656";
	setAttr ".v" no;
	setAttr ".hd" yes;
createNode joint -n "rig:TwistBalancerChest_M" -p "rig:UnTwistChest_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000657";
	setAttr ".t" -type "double3" 1.4210854715202004e-14 0 0 ;
	setAttr ".r" -type "double3" -4.2541805628289686e-14 1.1209339221423127e-13 -2.0371996812277815 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode transform -n "rig:TwistFollowOffsetKnee_R" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000659";
	setAttr ".t" -type "double3" -6.7944379482859354 44.36094860659751 -1.1956246606031948 ;
	setAttr ".r" -type "double3" 95.096475403272777 6.7905351051607106 -86.154733999027982 ;
	setAttr ".s" -type "double3" 0.99999999999999956 0.99999999999999967 1.0000000000000004 ;
createNode transform -n "rig:TwistFollowKnee_R" -p "rig:TwistFollowOffsetKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000065A";
	setAttr -l on ".v" no;
	setAttr ".ro" 2;
	setAttr ".s" -type "double3" 0.99999999999999989 1 1 ;
createNode parentConstraint -n "rig:TwistFollowKnee_R_parentConstraint1" -p "rig:TwistFollowKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000065B";
	addAttr -ci true -k true -sn "w0" -ln "FKXKnee_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -6.794436163111115 44.360948878047481 -1.1956449605891137 ;
	setAttr ".rsrr" -type "double3" 3.228439666591814 -95.068695671171767 -97.103402253556652 ;
	setAttr -k on ".w0";
createNode ikHandle -n "rig:UnTwistIKKnee_R" -p "rig:TwistFollowKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000065C";
	setAttr ".t" -type "double3" 1 1.7763568394002505e-15 -8.8817841970012523e-16 ;
	setAttr ".r" -type "double3" 32.555966007969744 96.007269630534708 129.51646588279462 ;
	setAttr ".s" -type "double3" 0.99999999999999978 1.0000000000000004 1.0000000000000004 ;
	setAttr ".roc" yes;
createNode poleVectorConstraint -n "rig:UnTwistIKKnee_R_poleVectorConstraint1" -p
		 "rig:UnTwistIKKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000065D";
	addAttr -ci true -k true -sn "w0" -ln "UnTwistKnee_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode transform -n "rig:TwistFollowParentOffsetKnee_R" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000065E";
	setAttr ".t" -type "double3" -8.8414397624647645 81.615172853450844 -1.9017649399230718 ;
	setAttr ".r" -type "double3" 95.061538946391465 -1.0842554986393318 -86.854940697119858 ;
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999978 0.99999999999999989 ;
createNode transform -n "rig:TwistFollowParentKnee_R" -p "rig:TwistFollowParentOffsetKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000065F";
	setAttr -l on ".v" no;
createNode parentConstraint -n "rig:TwistFollowParentKnee_R_parentConstraint1" -p
		 "rig:TwistFollowParentKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000660";
	addAttr -ci true -k true -sn "w0" -ln "FKXHip_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -8.8414397624647663 81.615172853450844 -1.9017649399230723 ;
	setAttr ".rsrr" -type "double3" 95.061538894162794 -1.0842243411384924 -86.854937936973286 ;
	setAttr -k on ".w0";
createNode joint -n "rig:UnTwistKnee_R" -p "rig:TwistFollowParentKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000661";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 -7.9057337300925967 ;
	setAttr ".ds" 2;
createNode joint -n "rig:UnTwistEndKnee_R" -p "rig:UnTwistKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000662";
	setAttr ".t" -type "double3" 1 0 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode pointConstraint -n "rig:UnTwistKnee_R_pointConstraint1" -p "rig:UnTwistKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000663";
	addAttr -ci true -k true -sn "w0" -ln "FKXKnee_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 37.317101082078786 -2.0372518044334265e-05 -2.6201263381153694e-13 ;
	setAttr -k on ".w0";
createNode ikEffector -n "rig:effector3" -p "rig:UnTwistKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000664";
	setAttr ".v" no;
	setAttr ".hd" yes;
createNode joint -n "rig:TwistBalancerKnee_R" -p "rig:UnTwistKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000665";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode parentConstraint -n "rig:TwistBalancerKnee_R_parentConstraint1" -p "rig:TwistBalancerKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000666";
	addAttr -ci true -k true -sn "w0" -ln "FKXKnee_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 2.2502079701780531e-06 -2.0255530766455365e-05 8.8817841970012523e-16 ;
	setAttr ".rsrr" -type "double3" 0 0 3.1221167515957951e-05 ;
	setAttr -k on ".w0";
createNode transform -n "rig:TwisterKnee0_R" -p "rig:UnTwistKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000667";
createNode transform -n "rig:TwisterKnee1_R" -p "rig:UnTwistKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000668";
createNode transform -n "rig:TwisterKnee2_R" -p "rig:UnTwistKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000669";
createNode transform -n "rig:TwistFollowOffsetHip_R" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000066A";
	setAttr ".t" -type "double3" -8.8414397624647645 81.615172853450844 -1.9017649399230718 ;
	setAttr ".r" -type "double3" 95.061538946391479 -1.0842554986393353 -86.854940697119872 ;
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999978 1.0000000000000007 ;
createNode transform -n "rig:TwistFollowHip_R" -p "rig:TwistFollowOffsetHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000066B";
	setAttr -l on ".v" no;
	setAttr ".ro" 2;
	setAttr ".s" -type "double3" 1.0000000000000002 1.0000000000000002 1.0000000000000002 ;
createNode parentConstraint -n "rig:TwistFollowHip_R_parentConstraint1" -p "rig:TwistFollowHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000066C";
	addAttr -ci true -k true -sn "w0" -ln "FKXHip_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -8.8414397624647663 81.615172853450844 -1.9017649399230723 ;
	setAttr ".rsrr" -type "double3" 3.2284396665918256 -95.068695671171767 -89.197731024106261 ;
	setAttr -k on ".w0";
createNode ikHandle -n "rig:UnTwistIKHip_R" -p "rig:TwistFollowHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000066D";
	setAttr ".t" -type "double3" 1 -4.3715031594615539e-16 -8.8817841970012523e-16 ;
	setAttr ".r" -type "double3" 32.555966007969616 96.007269630534722 121.61073215270174 ;
	setAttr ".s" -type "double3" 0.99999999999999933 1.0000000000000002 1.0000000000000002 ;
	setAttr ".roc" yes;
createNode poleVectorConstraint -n "rig:UnTwistIKHip_R_poleVectorConstraint1" -p "rig:UnTwistIKHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000066E";
	addAttr -ci true -k true -sn "w0" -ln "UnTwistHip_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode transform -n "rig:TwistFollowParentOffsetHip_R" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000066F";
	setAttr ".t" -type "double3" -5.8064397712757788e-15 88.867637422588331 0.47329046439253208 ;
	setAttr ".r" -type "double3" 89.999999999999972 -1.7514208112243506 89.999999999999986 ;
	setAttr ".s" -type "double3" 0.99999999999999978 0.99999999999999978 1 ;
createNode transform -n "rig:TwistFollowParentHip_R" -p "rig:TwistFollowParentOffsetHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000670";
	setAttr -l on ".v" no;
	setAttr ".s" -type "double3" 1.0000000000000004 1.0000000000000004 1 ;
createNode parentConstraint -n "rig:TwistFollowParentHip_R_parentConstraint1" -p "rig:TwistFollowParentHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000671";
	addAttr -ci true -k true -sn "w0" -ln "FKXRoot_MW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -2.0204353283577638e-15 88.867637422588331 0.47329046439253702 ;
	setAttr ".rsrr" -type "double3" 89.999999999999986 -1.7514208112243503 90.000000000000071 ;
	setAttr -k on ".w0";
createNode joint -n "rig:UnTwistHip_R" -p "rig:TwistFollowParentHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000672";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -174.87888821990936 -3.144495612966661 177.16268854732138 ;
	setAttr ".ds" 2;
createNode joint -n "rig:UnTwistEndHip_R" -p "rig:UnTwistHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000673";
	setAttr ".t" -type "double3" 1 0 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode pointConstraint -n "rig:UnTwistHip_R_pointConstraint1" -p "rig:UnTwistHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000674";
	addAttr -ci true -k true -sn "w0" -ln "FKXHip_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -7.3216659883418345 -2.1522866108679568 -8.8414397624647592 ;
	setAttr -k on ".w0";
createNode ikEffector -n "rig:effector4" -p "rig:UnTwistHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000675";
	setAttr ".v" no;
	setAttr ".hd" yes;
createNode joint -n "rig:TwistBalancerHip_R" -p "rig:UnTwistHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000676";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode parentConstraint -n "rig:TwistBalancerHip_R_parentConstraint1" -p "rig:TwistBalancerHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000677";
	addAttr -ci true -k true -sn "w0" -ln "FKXHip_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -1.4210854715202004e-14 -2.0122792321330962e-16 -8.8817841970012523e-16 ;
	setAttr ".rsrr" -type "double3" 0 0 -3.1279474723856088e-05 ;
	setAttr -k on ".w0";
createNode transform -n "rig:TwisterHip0_R" -p "rig:UnTwistHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000678";
createNode transform -n "rig:TwisterHip1_R" -p "rig:UnTwistHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000679";
createNode transform -n "rig:TwisterHip2_R" -p "rig:UnTwistHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000067A";
createNode transform -n "rig:TwistFollowOffsetWrist_R" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000067B";
	setAttr ".t" -type "double3" -20.987722480873085 78.841785267578814 1.9132525377466338 ;
	setAttr ".r" -type "double3" 83.562187684236761 -32.690834179111889 -93.414234120871328 ;
	setAttr ".s" -type "double3" 1 1.0000000000000002 1 ;
createNode transform -n "rig:TwistFollowWrist_R" -p "rig:TwistFollowOffsetWrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000067C";
	setAttr -l on ".v" no;
	setAttr ".t" -type "double3" -20.987722540896016 78.841784816983761 1.9132526054391923 ;
	setAttr ".r" -type "double3" -51.73383480996889 -81.235818965731667 -109.20479448398589 ;
	setAttr ".ro" 5;
	setAttr ".s" -type "double3" 0.99999999999999978 0.99999999999999978 0.99999999999999978 ;
createNode ikHandle -n "rig:UnTwistIKWrist_R" -p "rig:TwistFollowWrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000067E";
	setAttr ".t" -type "double3" 1.0000000000000071 0 3.5527136788005009e-15 ;
	setAttr ".r" -type "double3" 51.733832014335412 81.235819171498278 109.20479172099479 ;
	setAttr ".s" -type "double3" 1 0.99999999999999978 0.99999999999999978 ;
	setAttr ".roc" yes;
createNode poleVectorConstraint -n "rig:UnTwistIKWrist_R_poleVectorConstraint1" -p
		 "rig:UnTwistIKWrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000067F";
	addAttr -ci true -k true -sn "w0" -ln "UnTwistWrist_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode transform -n "rig:TwistFollowParentOffsetWrist_R" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000680";
	setAttr ".t" -type "double3" -19.053223849809221 99.96421895926278 -6.3430733567270119 ;
	setAttr ".r" -type "double3" 79.590780110652815 -21.268495760848555 -95.232837323714648 ;
	setAttr ".s" -type "double3" 0.99999999999999989 1 1 ;
createNode transform -n "rig:TwistFollowParentWrist_R" -p "rig:TwistFollowParentOffsetWrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000681";
	setAttr -l on ".v" no;
	setAttr ".t" -type "double3" -19.053223431736214 99.96421925826553 -6.3430712147746142 ;
	setAttr ".r" -type "double3" 79.5907805101739 -21.268490173576023 -95.232838425116029 ;
	setAttr ".s" -type "double3" 1.0000000000000002 1 1 ;
createNode joint -n "rig:UnTwistWrist_R" -p "rig:TwistFollowParentWrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000683";
	setAttr ".t" -type "double3" 22.761072638921704 -1.033720664622706e-07 3.3395508580724709e-13 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 4.7454770241091007 -0.5466259627365303 11.523286098605773 ;
	setAttr ".ds" 2;
createNode joint -n "rig:UnTwistEndWrist_R" -p "rig:UnTwistWrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000684";
	setAttr ".t" -type "double3" 1 0 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode ikEffector -n "rig:effector5" -p "rig:UnTwistWrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000686";
	setAttr ".v" no;
	setAttr ".hd" yes;
createNode joint -n "rig:TwistBalancerWrist_R" -p "rig:UnTwistWrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000687";
	setAttr ".t" -type "double3" 4.1811597384366905e-07 -1.9042219889797707e-07 1.1804889510358407e-08 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode transform -n "rig:TwisterWrist0_R" -p "rig:UnTwistWrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000689";
createNode transform -n "rig:TwisterWrist1_R" -p "rig:UnTwistWrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000068A";
createNode transform -n "rig:TwisterWrist2_R" -p "rig:UnTwistWrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000068B";
createNode transform -n "rig:TwistFollowOffsetElbow_R" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000068C";
	setAttr ".t" -type "double3" -19.053223849809221 99.96421895926278 -6.3430733567270119 ;
	setAttr ".r" -type "double3" 79.590780110652844 -21.268495760848566 -95.232837323714648 ;
	setAttr ".s" -type "double3" 0.99999999999999956 1.0000000000000007 1.0000000000000002 ;
createNode transform -n "rig:TwistFollowElbow_R" -p "rig:TwistFollowOffsetElbow_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000068D";
	setAttr -l on ".v" no;
	setAttr ".t" -type "double3" -19.053223431736214 99.96421925826553 -6.3430712147746142 ;
	setAttr ".r" -type "double3" -42.626221295602626 -76.771686676703226 -111.80289591650191 ;
	setAttr ".ro" 5;
	setAttr ".s" -type "double3" 1 0.99999999999999989 1.0000000000000002 ;
createNode ikHandle -n "rig:UnTwistIKElbow_R" -p "rig:TwistFollowElbow_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000068F";
	setAttr ".t" -type "double3" 1.0000000000000142 -7.1054273576010019e-15 0 ;
	setAttr ".r" -type "double3" 42.626221295602328 76.771686676703226 111.80289023573742 ;
	setAttr ".s" -type "double3" 0.99999999999999978 1.0000000000000004 0.99999999999999967 ;
	setAttr ".roc" yes;
createNode poleVectorConstraint -n "rig:UnTwistIKElbow_R_poleVectorConstraint1" -p
		 "rig:UnTwistIKElbow_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000690";
	addAttr -ci true -k true -sn "w0" -ln "UnTwistElbow_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode transform -n "rig:TwistFollowParentOffsetElbow_R" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000691";
	setAttr ".t" -type "double3" -14.32897626712335 128.14777525332582 -4.9690466428544493 ;
	setAttr ".r" -type "double3" 80.295538077017426 2.7527732444791906 -99.515696727980568 ;
createNode transform -n "rig:TwistFollowParentElbow_R" -p "rig:TwistFollowParentOffsetElbow_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000692";
	setAttr -l on ".v" no;
	setAttr ".t" -type "double3" -14.32897626712335 128.14777525332582 -4.9690466428544511 ;
	setAttr ".r" -type "double3" 80.29553811196088 2.7527689948275014 -99.515696000394115 ;
	setAttr ".s" -type "double3" 1 1 1.0000000000000002 ;
createNode joint -n "rig:UnTwistElbow_R" -p "rig:TwistFollowParentElbow_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000694";
	setAttr ".t" -type "double3" 28.609776009666447 2.1528047895458258e-06 -1.8474111129762605e-13 ;
	setAttr ".r" -type "double3" 4.7969267357504224 -21.90395990061975 -24.426623238474772 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 24.384535906822869 ;
	setAttr ".ds" 2;
createNode joint -n "rig:UnTwistEndElbow_R" -p "rig:UnTwistElbow_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000695";
	setAttr ".t" -type "double3" 1 0 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode ikEffector -n "rig:effector6" -p "rig:UnTwistElbow_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000697";
	setAttr ".v" no;
	setAttr ".hd" yes;
createNode joint -n "rig:TwistBalancerElbow_R" -p "rig:UnTwistElbow_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000698";
	setAttr ".t" -type "double3" 4.6396010588978243e-07 2.1533436260767758e-06 7.1054273576010019e-15 ;
	setAttr ".r" -type "double3" 0 0 -5.680764202436816e-06 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode transform -n "rig:TwisterElbow0_R" -p "rig:UnTwistElbow_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000069A";
createNode transform -n "rig:TwisterElbow1_R" -p "rig:UnTwistElbow_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000069B";
createNode transform -n "rig:TwisterElbow2_R" -p "rig:UnTwistElbow_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000069C";
createNode transform -n "rig:TwistFollowOffsetShoulder_R" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000069D";
	setAttr ".t" -type "double3" -14.32897626712335 128.14777525332582 -4.9690466428544493 ;
	setAttr ".r" -type "double3" 80.295538077017426 2.7527732444791879 -99.515696727980583 ;
	setAttr ".s" -type "double3" 0.99999999999999956 1 1 ;
createNode transform -n "rig:TwistFollowShoulder_R" -p "rig:TwistFollowOffsetShoulder_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000069E";
	setAttr -l on ".v" no;
	setAttr ".t" -type "double3" -14.32897626712335 128.14777525332582 -4.9690466428544511 ;
	setAttr ".r" -type "double3" -42.626221295602583 -76.771686676703226 -136.187421831215 ;
	setAttr ".ro" 5;
	setAttr ".s" -type "double3" 1.0000000000000004 1.0000000000000002 1.0000000000000004 ;
createNode ikHandle -n "rig:UnTwistIKShoulder_R" -p "rig:TwistFollowShoulder_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006A0";
	setAttr ".t" -type "double3" 1 3.5527136788005009e-15 7.1054273576010019e-15 ;
	setAttr ".r" -type "double3" 42.626221295602356 76.771686676703155 136.18742614256035 ;
	setAttr ".s" -type "double3" 0.99999999999999956 1 0.99999999999999967 ;
	setAttr ".roc" yes;
createNode poleVectorConstraint -n "rig:UnTwistIKShoulder_R_poleVectorConstraint1" 
		-p "rig:UnTwistIKShoulder_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006A1";
	addAttr -ci true -k true -sn "w0" -ln "UnTwistShoulder_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode transform -n "rig:TwistFollowParentOffsetShoulder_R" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006A2";
	setAttr ".t" -type "double3" -1.1096741025742629 127.6238117117818 0.74229571841643605 ;
	setAttr ".r" -type "double3" 85.356850077671226 23.35018097290142 177.73019840896941 ;
createNode transform -n "rig:TwistFollowParentShoulder_R" -p "rig:TwistFollowParentOffsetShoulder_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006A3";
	setAttr -l on ".v" no;
	setAttr ".t" -type "double3" -1.1096741025742629 127.6238117117818 0.74229571841643605 ;
	setAttr ".r" -type "double3" 85.356850077671226 23.350180972901427 177.73019840896941 ;
createNode joint -n "rig:UnTwistShoulder_R" -p "rig:TwistFollowParentShoulder_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006A5";
	setAttr ".t" -type "double3" 14.409854929115932 -4.1744385725905886e-14 3.5527136788005009e-13 ;
	setAttr ".r" -type "double3" -11.082130937457752 -52.45495768636966 22.279957595992563 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 80.803017877340892 32.565954645224288 ;
	setAttr ".ds" 2;
createNode joint -n "rig:UnTwistEndShoulder_R" -p "rig:UnTwistShoulder_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006A6";
	setAttr ".t" -type "double3" 1 0 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode ikEffector -n "rig:effector7" -p "rig:UnTwistShoulder_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006A8";
	setAttr ".v" no;
	setAttr ".hd" yes;
createNode joint -n "rig:TwistBalancerShoulder_R" -p "rig:UnTwistShoulder_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006A9";
	setAttr ".r" -type "double3" 0 0 4.3113455653541671e-06 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode transform -n "rig:TwisterShoulder0_R" -p "rig:UnTwistShoulder_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006AB";
createNode transform -n "rig:TwisterShoulder1_R" -p "rig:UnTwistShoulder_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006AC";
createNode transform -n "rig:TwisterShoulder2_R" -p "rig:UnTwistShoulder_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006AD";
createNode transform -n "rig:TwistFollowOffsetKnee_L" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006AE";
	setAttr ".t" -type "double3" 6.7944379482859567 44.360948606597532 -1.1956246606031984 ;
	setAttr ".r" -type "double3" -84.903524596727266 -6.7905351051608749 86.154733999028082 ;
	setAttr ".s" -type "double3" 0.99999999999999989 1 1.0000000000000004 ;
createNode transform -n "rig:TwistFollowKnee_L" -p "rig:TwistFollowOffsetKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006AF";
	setAttr -l on ".v" no;
	setAttr ".ro" 2;
	setAttr ".s" -type "double3" 1 1 1.0000000000000002 ;
createNode parentConstraint -n "rig:TwistFollowKnee_L_parentConstraint1" -p "rig:TwistFollowKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006B0";
	addAttr -ci true -k true -sn "w0" -ln "FKXKnee_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 6.7944361634493564 44.360948878100515 -1.1956449568097667 ;
	setAttr ".rsrr" -type "double3" -3.2284396665917203 -84.931304328828261 82.896597752267482 ;
	setAttr -k on ".w0";
createNode ikHandle -n "rig:UnTwistIKKnee_L" -p "rig:TwistFollowKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006B1";
	setAttr ".t" -type "double3" -0.99999999999997868 1.7763568394002505e-15 1.7763568394002505e-15 ;
	setAttr ".r" -type "double3" 32.555966007969062 83.992730369465392 -50.483534117205899 ;
	setAttr ".s" -type "double3" 0.99999999999999944 1 1 ;
	setAttr ".roc" yes;
createNode poleVectorConstraint -n "rig:UnTwistIKKnee_L_poleVectorConstraint1" -p
		 "rig:UnTwistIKKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006B2";
	addAttr -ci true -k true -sn "w0" -ln "UnTwistKnee_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode transform -n "rig:TwistFollowParentOffsetKnee_L" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006B3";
	setAttr ".t" -type "double3" 8.8414397624647396 81.615172853450844 -1.9017649399230718 ;
	setAttr ".r" -type "double3" -84.938461053608535 1.0842554986392077 86.854940697119957 ;
	setAttr ".s" -type "double3" 1 0.99999999999999989 1 ;
createNode transform -n "rig:TwistFollowParentKnee_L" -p "rig:TwistFollowParentOffsetKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006B4";
	setAttr -l on ".v" no;
	setAttr ".s" -type "double3" 1 0.99999999999999989 1 ;
createNode parentConstraint -n "rig:TwistFollowParentKnee_L_parentConstraint1" -p
		 "rig:TwistFollowParentKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006B5";
	addAttr -ci true -k true -sn "w0" -ln "FKXHip_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 8.8414397624647378 81.615172853450844 -1.9017649399230718 ;
	setAttr ".rsrr" -type "double3" -84.938461105827486 1.0842243469421391 86.85493793748752 ;
	setAttr -k on ".w0";
createNode joint -n "rig:UnTwistKnee_L" -p "rig:TwistFollowParentKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006B6";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 -7.9057337300926926 ;
	setAttr ".ds" 2;
createNode joint -n "rig:UnTwistEndKnee_L" -p "rig:UnTwistKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006B7";
	setAttr ".t" -type "double3" -1 0 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode pointConstraint -n "rig:UnTwistKnee_L_pointConstraint1" -p "rig:UnTwistKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006B8";
	addAttr -ci true -k true -sn "w0" -ln "FKXKnee_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -37.317101082078779 2.0368723138604328e-05 2.6734170432973769e-13 ;
	setAttr -k on ".w0";
createNode ikEffector -n "rig:effector8" -p "rig:UnTwistKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006B9";
	setAttr ".v" no;
	setAttr ".hd" yes;
createNode joint -n "rig:TwistBalancerKnee_L" -p "rig:UnTwistKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006BA";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode parentConstraint -n "rig:TwistBalancerKnee_L_parentConstraint1" -p "rig:TwistBalancerKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006BB";
	addAttr -ci true -k true -sn "w0" -ln "FKXKnee_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -2.2496860623277826e-06 2.0251772002488622e-05 -1.7763568394002505e-15 ;
	setAttr ".rsrr" -type "double3" 0 0 3.1226991810109033e-05 ;
	setAttr -k on ".w0";
createNode transform -n "rig:TwisterKnee0_L" -p "rig:UnTwistKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006BC";
createNode transform -n "rig:TwisterKnee1_L" -p "rig:UnTwistKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006BD";
createNode transform -n "rig:TwisterKnee2_L" -p "rig:UnTwistKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006BE";
createNode transform -n "rig:TwistFollowOffsetHip_L" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006BF";
	setAttr ".t" -type "double3" 8.8414397624647396 81.615172853450844 -1.9017649399230718 ;
	setAttr ".r" -type "double3" -84.938461053608549 1.0842554986392015 86.854940697119957 ;
	setAttr ".s" -type "double3" 0.99999999999999967 0.99999999999999989 1.0000000000000004 ;
createNode transform -n "rig:TwistFollowHip_L" -p "rig:TwistFollowOffsetHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006C0";
	setAttr -l on ".v" no;
	setAttr ".ro" 2;
	setAttr ".s" -type "double3" 1 1 0.99999999999999989 ;
createNode parentConstraint -n "rig:TwistFollowHip_L_parentConstraint1" -p "rig:TwistFollowHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006C1";
	addAttr -ci true -k true -sn "w0" -ln "FKXHip_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 8.8414397624647378 81.615172853450844 -1.9017649399230718 ;
	setAttr ".rsrr" -type "double3" -3.228439666591735 -84.931304328828233 90.802268981720133 ;
	setAttr -k on ".w0";
createNode ikHandle -n "rig:UnTwistIKHip_L" -p "rig:TwistFollowHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006C2";
	setAttr ".t" -type "double3" -0.99999999999998579 2.2898349882893854e-16 8.8817841970012523e-16 ;
	setAttr ".r" -type "double3" 32.555966007969012 83.99273036946532 -58.389267847298761 ;
	setAttr ".s" -type "double3" 0.99999999999999967 1.0000000000000004 1.0000000000000002 ;
	setAttr ".roc" yes;
createNode poleVectorConstraint -n "rig:UnTwistIKHip_L_poleVectorConstraint1" -p "rig:UnTwistIKHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006C3";
	addAttr -ci true -k true -sn "w0" -ln "UnTwistHip_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode transform -n "rig:TwistFollowParentOffsetHip_L" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006C4";
	setAttr ".t" -type "double3" -5.8064397712757788e-15 88.867637422588331 0.47329046439253208 ;
	setAttr ".r" -type "double3" 89.999999999999972 -1.7514208112243506 89.999999999999986 ;
	setAttr ".s" -type "double3" 0.99999999999999978 0.99999999999999978 1 ;
createNode transform -n "rig:TwistFollowParentHip_L" -p "rig:TwistFollowParentOffsetHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006C5";
	setAttr -l on ".v" no;
	setAttr ".s" -type "double3" 1.0000000000000004 1.0000000000000004 1 ;
createNode parentConstraint -n "rig:TwistFollowParentHip_L_parentConstraint1" -p "rig:TwistFollowParentHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006C6";
	addAttr -ci true -k true -sn "w0" -ln "FKXRoot_MW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -2.0204353283577638e-15 88.867637422588331 0.47329046439253702 ;
	setAttr ".rsrr" -type "double3" 89.999999999999986 -1.7514208112243503 90.000000000000071 ;
	setAttr -k on ".w0";
createNode joint -n "rig:UnTwistHip_L" -p "rig:TwistFollowParentHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006C7";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -174.87888821990933 -3.1444956129665536 -2.8373114526785552 ;
	setAttr ".ds" 2;
createNode joint -n "rig:UnTwistEndHip_L" -p "rig:UnTwistHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006C8";
	setAttr ".t" -type "double3" -1 0 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode pointConstraint -n "rig:UnTwistHip_L_pointConstraint1" -p "rig:UnTwistHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006C9";
	addAttr -ci true -k true -sn "w0" -ln "FKXHip_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -7.3216659883418345 -2.1522866108679657 8.8414397624647449 ;
	setAttr -k on ".w0";
createNode ikEffector -n "rig:effector9" -p "rig:UnTwistHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006CA";
	setAttr ".v" no;
	setAttr ".hd" yes;
createNode joint -n "rig:TwistBalancerHip_L" -p "rig:UnTwistHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006CB";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode parentConstraint -n "rig:TwistBalancerHip_L_parentConstraint1" -p "rig:TwistBalancerHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006CC";
	addAttr -ci true -k true -sn "w0" -ln "FKXHip_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 0 -2.4286128663675299e-16 3.5527136788005009e-15 ;
	setAttr ".rsrr" -type "double3" 0 0 -3.1273648249534168e-05 ;
	setAttr -k on ".w0";
createNode transform -n "rig:TwisterHip0_L" -p "rig:UnTwistHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006CD";
createNode transform -n "rig:TwisterHip1_L" -p "rig:UnTwistHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006CE";
createNode transform -n "rig:TwisterHip2_L" -p "rig:UnTwistHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006CF";
createNode transform -n "rig:TwistFollowOffsetWrist_L" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006D0";
	setAttr ".t" -type "double3" 20.987722480873309 78.84178526757907 1.9132525377467502 ;
	setAttr ".r" -type "double3" -96.437812315763068 32.69083417911164 93.414234120871797 ;
	setAttr ".s" -type "double3" 0.99999999999999956 0.99999999999999944 1 ;
createNode transform -n "rig:TwistFollowWrist_L" -p "rig:TwistFollowOffsetWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006D1";
	setAttr -l on ".v" no;
	setAttr ".ro" 5;
	setAttr ".s" -type "double3" 1 1 0.99999999999999989 ;
createNode parentConstraint -n "rig:TwistFollowWrist_L_parentConstraint1" -p "rig:TwistFollowWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006D2";
	addAttr -ci true -k true -sn "w0" -ln "FKXWrist_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 20.987722639851206 78.841784833186551 1.9132526237052034 ;
	setAttr ".rsrr" -type "double3" 128.26616701606616 -81.235819595622019 -109.20479267927229 ;
	setAttr -k on ".w0";
createNode ikHandle -n "rig:UnTwistIKWrist_L" -p "rig:TwistFollowWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006D3";
	setAttr ".t" -type "double3" -1 0 -3.5527136788005009e-15 ;
	setAttr ".r" -type "double3" -128.26616798566246 81.235819171498065 109.20479172099722 ;
	setAttr ".s" -type "double3" 0.99999999999999989 1.0000000000000004 1.0000000000000002 ;
	setAttr ".roc" yes;
createNode poleVectorConstraint -n "rig:UnTwistIKWrist_L_poleVectorConstraint1" -p
		 "rig:UnTwistIKWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006D4";
	addAttr -ci true -k true -sn "w0" -ln "UnTwistWrist_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode transform -n "rig:TwistFollowParentOffsetWrist_L" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006D5";
	setAttr ".t" -type "double3" 19.053223849809399 99.964218959262993 -6.3430733567268938 ;
	setAttr ".r" -type "double3" -100.40921988934706 21.268495760848413 95.232837323715032 ;
	setAttr ".s" -type "double3" 1 0.99999999999999989 0.99999999999999989 ;
createNode transform -n "rig:TwistFollowParentWrist_L" -p "rig:TwistFollowParentOffsetWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006D6";
	setAttr -l on ".v" no;
	setAttr ".s" -type "double3" 1 1 1.0000000000000002 ;
createNode parentConstraint -n "rig:TwistFollowParentWrist_L_parentConstraint1" -p
		 "rig:TwistFollowParentWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006D7";
	addAttr -ci true -k true -sn "w0" -ln "FKXElbow_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 19.053223431736424 99.964219258265771 -6.3430712147744961 ;
	setAttr ".rsrr" -type "double3" -100.40921882585585 21.268490222916544 95.23283869529601 ;
	setAttr -k on ".w0";
createNode joint -n "rig:UnTwistWrist_L" -p "rig:TwistFollowParentWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006D8";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 4.7454770241091397 -0.54662596273652075 11.52328609860567 ;
	setAttr ".ds" 2;
createNode joint -n "rig:UnTwistEndWrist_L" -p "rig:UnTwistWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006D9";
	setAttr ".t" -type "double3" -1 0 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode pointConstraint -n "rig:UnTwistWrist_L_pointConstraint1" -p "rig:UnTwistWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006DA";
	addAttr -ci true -k true -sn "w0" -ln "FKXWrist_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -22.761072638921704 1.0216508883331699e-07 -1.0191588017960385e-07 ;
	setAttr -k on ".w0";
createNode ikEffector -n "rig:effector10" -p "rig:UnTwistWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006DB";
	setAttr ".v" no;
	setAttr ".hd" yes;
createNode joint -n "rig:TwistBalancerWrist_L" -p "rig:UnTwistWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006DC";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode parentConstraint -n "rig:TwistBalancerWrist_L_parentConstraint1" -p "rig:TwistBalancerWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006DD";
	addAttr -ci true -k true -sn "w0" -ln "FKXWrist_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -4.1932939609523601e-07 1.8081281893955747e-07 -1.1326639182129838e-07 ;
	setAttr -k on ".w0";
createNode transform -n "rig:TwisterWrist0_L" -p "rig:UnTwistWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006DE";
createNode transform -n "rig:TwisterWrist1_L" -p "rig:UnTwistWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006DF";
createNode transform -n "rig:TwisterWrist2_L" -p "rig:UnTwistWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006E0";
createNode transform -n "rig:TwistFollowOffsetElbow_L" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006E1";
	setAttr ".t" -type "double3" 19.053223849809399 99.964218959262993 -6.3430733567268938 ;
	setAttr ".r" -type "double3" -100.40921988934703 21.268495760848367 95.232837323715003 ;
	setAttr ".s" -type "double3" 0.99999999999999967 0.99999999999999967 1.0000000000000004 ;
createNode transform -n "rig:TwistFollowElbow_L" -p "rig:TwistFollowOffsetElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006E2";
	setAttr -l on ".v" no;
	setAttr ".ro" 5;
	setAttr ".s" -type "double3" 1.0000000000000002 1.0000000000000002 1.0000000000000002 ;
createNode parentConstraint -n "rig:TwistFollowElbow_L_parentConstraint1" -p "rig:TwistFollowElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006E3";
	addAttr -ci true -k true -sn "w0" -ln "FKXElbow_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 19.053223431736424 99.964219258265771 -6.3430712147744961 ;
	setAttr ".rsrr" -type "double3" 137.37377674485654 -76.771687106897332 -111.80289782101032 ;
	setAttr -k on ".w0";
createNode ikHandle -n "rig:UnTwistIKElbow_L" -p "rig:TwistFollowElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006E4";
	setAttr ".t" -type "double3" -1.0000000000000142 7.1054273576010019e-15 7.1054273576010019e-15 ;
	setAttr ".r" -type "double3" -137.37377870439647 76.771686676703098 111.80289023573876 ;
	setAttr ".s" -type "double3" 0.99999999999999911 0.99999999999999989 1 ;
	setAttr ".roc" yes;
createNode poleVectorConstraint -n "rig:UnTwistIKElbow_L_poleVectorConstraint1" -p
		 "rig:UnTwistIKElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006E5";
	addAttr -ci true -k true -sn "w0" -ln "UnTwistElbow_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode transform -n "rig:TwistFollowParentOffsetElbow_L" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006E6";
	setAttr ".t" -type "double3" 14.328976267123249 128.14777525332596 -4.9690466428543738 ;
	setAttr ".r" -type "double3" -99.704461922982446 -2.7527732444791222 99.51569672798081 ;
	setAttr ".s" -type "double3" 1.0000000000000002 1 1 ;
createNode transform -n "rig:TwistFollowParentElbow_L" -p "rig:TwistFollowParentOffsetElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006E7";
	setAttr -l on ".v" no;
	setAttr ".s" -type "double3" 0.99999999999999978 1.0000000000000002 1 ;
createNode parentConstraint -n "rig:TwistFollowParentElbow_L_parentConstraint1" -p
		 "rig:TwistFollowParentElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006E8";
	addAttr -ci true -k true -sn "w0" -ln "FKXShoulder_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 14.32897626712324 128.14777525332596 -4.9690466428543738 ;
	setAttr ".rsrr" -type "double3" -99.704461266641928 -2.752768994827417 99.515696000394414 ;
	setAttr -k on ".w0";
createNode joint -n "rig:UnTwistElbow_L" -p "rig:TwistFollowParentElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006E9";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 24.384535906822652 ;
	setAttr ".ds" 2;
createNode joint -n "rig:UnTwistEndElbow_L" -p "rig:UnTwistElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006EA";
	setAttr ".t" -type "double3" -1 0 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode pointConstraint -n "rig:UnTwistElbow_L_pointConstraint1" -p "rig:UnTwistElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006EB";
	addAttr -ci true -k true -sn "w0" -ln "FKXElbow_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -28.609776009666405 -2.1528047611241163e-06 -7.1054273576010019e-15 ;
	setAttr -k on ".w0";
createNode ikEffector -n "rig:effector11" -p "rig:UnTwistElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006EC";
	setAttr ".v" no;
	setAttr ".hd" yes;
createNode joint -n "rig:TwistBalancerElbow_L" -p "rig:UnTwistElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006ED";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode parentConstraint -n "rig:TwistBalancerElbow_L_parentConstraint1" -p "rig:TwistBalancerElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006EE";
	addAttr -ci true -k true -sn "w0" -ln "FKXElbow_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -4.6396010588978243e-07 -2.1533436367349168e-06 -3.5527136788005009e-14 ;
	setAttr ".rsrr" -type "double3" 0 0 -5.677726162049524e-06 ;
	setAttr -k on ".w0";
createNode transform -n "rig:TwisterElbow0_L" -p "rig:UnTwistElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006EF";
createNode transform -n "rig:TwisterElbow1_L" -p "rig:UnTwistElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006F0";
createNode transform -n "rig:TwisterElbow2_L" -p "rig:UnTwistElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006F1";
createNode transform -n "rig:TwistFollowOffsetShoulder_L" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006F2";
	setAttr ".t" -type "double3" 14.328976267123249 128.14777525332596 -4.9690466428543738 ;
	setAttr ".r" -type "double3" -99.704461922982418 -2.7527732444791266 99.515696727980796 ;
	setAttr ".s" -type "double3" 0.99999999999999967 0.99999999999999989 1.0000000000000002 ;
createNode transform -n "rig:TwistFollowShoulder_L" -p "rig:TwistFollowOffsetShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006F3";
	setAttr -l on ".v" no;
	setAttr ".ro" 5;
	setAttr ".s" -type "double3" 0.99999999999999978 0.99999999999999989 1 ;
createNode parentConstraint -n "rig:TwistFollowShoulder_L_parentConstraint1" -p "rig:TwistFollowShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006F4";
	addAttr -ci true -k true -sn "w0" -ln "FKXShoulder_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 14.32897626712324 128.14777525332596 -4.9690466428543738 ;
	setAttr ".rsrr" -type "double3" 137.3737767448564 -76.771687106897289 -136.18742373876148 ;
	setAttr -k on ".w0";
createNode ikHandle -n "rig:UnTwistIKShoulder_L" -p "rig:TwistFollowShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006F5";
	setAttr ".t" -type "double3" -1 0 -7.1054273576010019e-15 ;
	setAttr ".r" -type "double3" -137.37377870439639 76.771686676703112 136.18742614256146 ;
	setAttr ".s" -type "double3" 0.99999999999999978 1.0000000000000004 1.0000000000000002 ;
	setAttr ".roc" yes;
createNode poleVectorConstraint -n "rig:UnTwistIKShoulder_L_poleVectorConstraint1" 
		-p "rig:UnTwistIKShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006F6";
	addAttr -ci true -k true -sn "w0" -ln "UnTwistShoulder_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode transform -n "rig:TwistFollowParentOffsetShoulder_L" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006F7";
	setAttr ".t" -type "double3" 1.1096741025741184 127.62381171178184 0.7422957184164356 ;
	setAttr ".r" -type "double3" 85.356850077671297 203.35018097290131 2.2698015910308107 ;
	setAttr ".s" -type "double3" 0.99999999999999989 1 1 ;
createNode transform -n "rig:TwistFollowParentShoulder_L" -p "rig:TwistFollowParentOffsetShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006F8";
	setAttr -l on ".v" no;
	setAttr ".s" -type "double3" 1.0000000000000002 1 1 ;
createNode parentConstraint -n "rig:TwistFollowParentShoulder_L_parentConstraint1" 
		-p "rig:TwistFollowParentShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006F9";
	addAttr -ci true -k true -sn "w0" -ln "FKXScapula_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 1.1096741025741184 127.62381171178184 0.7422957184164356 ;
	setAttr ".rsrr" -type "double3" 85.356850077671311 203.35018097290131 2.2698015910308107 ;
	setAttr -k on ".w0";
createNode joint -n "rig:UnTwistShoulder_L" -p "rig:TwistFollowParentShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006FA";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 80.803017877340906 32.565954645224309 ;
	setAttr ".ds" 2;
createNode joint -n "rig:UnTwistEndShoulder_L" -p "rig:UnTwistShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006FB";
	setAttr ".t" -type "double3" -1 0 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode pointConstraint -n "rig:UnTwistShoulder_L_pointConstraint1" -p "rig:UnTwistShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006FC";
	addAttr -ci true -k true -sn "w0" -ln "FKXShoulder_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -14.409854929115941 -1.7763568394002505e-14 -4.4053649617126212e-13 ;
	setAttr -k on ".w0";
createNode ikEffector -n "rig:effector12" -p "rig:UnTwistShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006FD";
	setAttr ".v" no;
	setAttr ".hd" yes;
createNode joint -n "rig:TwistBalancerShoulder_L" -p "rig:UnTwistShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006FE";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode parentConstraint -n "rig:TwistBalancerShoulder_L_parentConstraint1" -p
		 "rig:TwistBalancerShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000006FF";
	addAttr -ci true -k true -sn "w0" -ln "FKXShoulder_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -1.4210854715202004e-14 -3.5527136788005009e-15 1.4210854715202004e-14 ;
	setAttr ".rsrr" -type "double3" 6.2139727288844783e-07 7.0137584492700507e-14 4.3113455776788192e-06 ;
	setAttr -k on ".w0";
createNode transform -n "rig:TwisterShoulder0_L" -p "rig:UnTwistShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000700";
createNode transform -n "rig:TwisterShoulder1_L" -p "rig:UnTwistShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000701";
createNode transform -n "rig:TwisterShoulder2_L" -p "rig:UnTwistShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000702";
createNode transform -n "rig:FKIKMixKnee_R" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000703";
createNode pointConstraint -n "rig:FKIKMixKnee_R_pointConstraint1" -p "rig:FKIKMixKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000704";
	addAttr -ci true -k true -sn "w0" -ln "FKXKnee_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -6.794436163111115 44.360948878047495 -1.1956449605891133 ;
	setAttr -k on ".w0";
createNode transform -n "rig:FKIKMixKnee_L" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000709";
createNode pointConstraint -n "rig:FKIKMixKnee_L_pointConstraint1" -p "rig:FKIKMixKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000070A";
	addAttr -ci true -k true -sn "w0" -ln "FKXKnee_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 6.7944361634493573 44.36094887810053 -1.1956449568097662 ;
	setAttr -k on ".w0";
createNode transform -n "rig:FKIKMixWrist_L" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000070B";
createNode pointConstraint -n "rig:FKIKMixWrist_L_pointConstraint1" -p "rig:FKIKMixWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000070C";
	addAttr -ci true -k true -sn "w0" -ln "FKXWrist_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 20.987722639851206 78.841784833186537 1.9132526237051981 ;
	setAttr -k on ".w0";
createNode transform -n "rig:FKIKMixElbow_L" -p "rig:TwistSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000070D";
createNode pointConstraint -n "rig:FKIKMixElbow_L_pointConstraint1" -p "rig:FKIKMixElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000070E";
	addAttr -ci true -k true -sn "w0" -ln "FKXElbow_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 19.053223431736427 99.964219258265757 -6.3430712147744917 ;
	setAttr -k on ".w0";
createNode transform -n "rig:GlobalSystem" -p "rig:MotionSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000070F";
createNode transform -n "rig:GlobalOffsetHead_M" -p "rig:GlobalSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000710";
	setAttr ".t" -type "double3" -1.1053770371298738e-13 143.65649237269602 0.32023587761594752 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 90.000000000000014 ;
	setAttr ".ro" 5;
createNode transform -n "rig:GlobalHead_M" -p "rig:GlobalOffsetHead_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000711";
	setAttr ".ro" 5;
createNode transform -n "rig:ConstraintSystem" -p "rig:MotionSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000712";
createNode parentConstraint -n "rig:Ankle_R_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000714";
	addAttr -ci true -k true -sn "w0" -ln "FKXAnkle_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -4.308196705432108 7.3707391755914173 -5.6101808417093402 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 101.00958441533642 3.6228505668545372e-14 -89.999999999999304 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999967 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 1.9257264672923664e-14 2.6985018625542042e-14 -1.1365513369542286e-13 ;
	setAttr ".rst" -type "double3" 37.335576807429952 -1.8207657603852567e-13 1.865174681370263e-14 ;
	setAttr ".rsrr" -type "double3" -3.8564225512745173e-14 -5.1485228906190697e-14 -7.7600564611019994e-14 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:Knee_R_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000715";
	addAttr -ci true -k true -sn "w0" -ln "FKXKnee_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -6.7944379482859274 44.360948606597503 -1.1956246606031848 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 95.096475403272791 6.7905351051606351 -86.154733999027982 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999978 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 0 0 -1.5902773407317584e-14 ;
	setAttr ".rst" -type "double3" 12.43903387975913 3.4867941867133823e-14 -2.6467716907063732e-13 ;
	setAttr ".rsrr" -type "double3" 0 0 -7.4743035014392642e-14 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:IndexFinger3_R_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000717";
	addAttr -ci true -k true -sn "w0" -ln "FKXIndexFinger3_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -19.562273258199813 66.942876823789632 7.6258767233292977 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 55.432741399046805 1.1072080726913038 -49.338654446196848 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999967 0.99999999999999989 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" -133.22055281293532 3.9362905349827879 -4.2769741637597063 ;
	setAttr ".rst" -type "double3" 2.2798674841394302 1.4210854715202004e-14 -6.9277916736609768e-14 ;
	setAttr ".rsrr" -type "double3" -1.1454966469958447e-14 -4.7114295727001669e-15 -5.9262679025706937e-15 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:IndexFinger2_R_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000718";
	addAttr -ci true -k true -sn "w0" -ln "FKXIndexFinger2_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -20.898578640500851 68.787898991244816 7.5365633868756596 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 57.11232521916132 -2.2451247966113983 -54.085085568973604 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999989 0.99999999999999989 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 48.296333789194541 -18.745806965454797 19.806079730705051 ;
	setAttr ".rst" -type "double3" 2.6150711681148238 1.4210854715202004e-14 2.8421709430404007e-14 ;
	setAttr ".rsrr" -type "double3" 9.5043919192170862e-16 2.862482833965282e-14 2.5068416063891061e-14 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:IndexFinger1_R_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000719";
	addAttr -ci true -k true -sn "w0" -ln "FKXIndexFinger1_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -21.441355545624202 71.238180029320063 6.8016393907923156 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 60.967409053203426 -16.321928696134325 -77.509747392326403 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999967 0.99999999999999989 0.99999999999999989 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 37.654597922071837 -59.558130727162208 117.10391734309019 ;
	setAttr ".rst" -type "double3" 9.0507967385055395 7.1054273576010019e-15 -7.460698725481052e-14 ;
	setAttr ".rsrr" -type "double3" 3.3793393490549872e-15 -5.1684013573782151e-15 1.9480897423964044e-14 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:MiddleFinger3_R_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000071A";
	addAttr -ci true -k true -sn "w0" -ln "FKXMiddleFinger3_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -19.620031198118575 66.254357780639126 5.7813841133156627 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 69.238813797673544 3.6084453984109768 -31.149533637609181 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999989 1 0.99999999999999956 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 133.94074192506602 10.60216580010384 10.810743156637045 ;
	setAttr ".rst" -type "double3" 2.3283439685011373 -1.4210854715202004e-14 -3.5527136788005009e-14 ;
	setAttr ".rsrr" -type "double3" -4.8981202121754775e-14 -4.1334445580803701e-14 1.4060132719057578e-14 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:MiddleFinger2_R_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000071B";
	addAttr -ci true -k true -sn "w0" -ln "FKXMiddleFinger2_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -21.258317267545969 67.907195852926748 5.7083724897716817 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 68.961276780780395 -1.796961195031 -45.253336816843401 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999956 1 0.99999999999999978 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 47.550540663357019 -16.8491663521162 20.304864266695724 ;
	setAttr ".rst" -type "double3" 2.9299735768953639 -1.4210854715202004e-14 -2.2204460492503131e-15 ;
	setAttr ".rsrr" -type "double3" -2.3059021440610504e-14 3.0951393946078006e-15 3.361945690640733e-14 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:MiddleFinger1_R_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000071C";
	addAttr -ci true -k true -sn "w0" -ln "FKXMiddleFinger1_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -22.268035647683625 70.583032347115079 5.0718876034726073 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 71.536483424612584 -12.546524219572239 -69.326160786587096 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999956 0.99999999999999989 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" -5.7975521398123924 18.039490857094549 105.36387077759646 ;
	setAttr ".rst" -type "double3" 8.7083736116588426 -1.9121430819272192 0.57542589341596084 ;
	setAttr ".rsrr" -type "double3" 3.1805546814635168e-15 5.9635400277441008e-16 2.5742614453095339e-14 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:PinkyFinger3_R_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000071D";
	addAttr -ci true -k true -sn "w0" -ln "FKXPinkyFinger3_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -20.688219056474679 67.443390865608933 1.991208252354487 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 99.785786639930308 -16.101211220081371 -31.964319913019708 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999978 0.99999999999999978 0.99999999999999944 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" -49.108139321133287 -14.121838181047497 -15.695857406330839 ;
	setAttr ".rst" -type "double3" 1.5833293982735057 3.907985046680551e-14 -9.2370555648813024e-14 ;
	setAttr ".rsrr" -type "double3" 1.30452438106902e-14 -4.1747109702031997e-14 -1.7095481412866397e-14 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:PinkyFinger2_R_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000071E";
	addAttr -ci true -k true -sn "w0" -ln "FKXPinkyFinger2_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -21.619632343749288 68.683657520732396 1.6731832597608434 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 102.74854120242783 -11.587159779955543 -53.094247303278465 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999967 0.99999999999999978 0.99999999999999956 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" -47.703762150646661 -16.245144833353166 -16.984562437581044 ;
	setAttr ".rst" -type "double3" 2.1075383328535366 -1.9539925233402755e-14 3.5305092183079978e-14 ;
	setAttr ".rsrr" -type "double3" -2.2645922053271968e-14 -3.1906067503782811e-15 -7.0009475117370756e-15 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:PinkyFinger1_R_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000071F";
	addAttr -ci true -k true -sn "w0" -ln "FKXPinkyFinger1_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -22.128309577958213 70.717988068964203 1.4623171496921317 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 105.9812909580608 -5.7422382323428769 -75.961249005882436 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999944 0.99999999999999967 0.99999999999999978 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" -72.296303760778997 -26.903686121725599 -6.0652852983756622 ;
	setAttr ".rst" -type "double3" 4.5250926779440022 -2.3533218848592057 -0.44446663353526361 ;
	setAttr ".rsrr" -type "double3" 2.4251729446159314e-14 -1.0336802714756432e-14 -1.3517357396219944e-14 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:RingFinger3_R_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000720";
	addAttr -ci true -k true -sn "w0" -ln "FKXRingFinger3_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -20.140333889320324 66.444882956127771 4.0237414379298091 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 79.948334859010288 -5.600086268018611 -35.613813547935784 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999978 0.99999999999999978 0.99999999999999967 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" -45.973098860584194 -6.7284295046079698 -6.9235381680522012 ;
	setAttr ".rst" -type "double3" 2.2923824975696263 2.4868995751603507e-14 4.6185277824406512e-14 ;
	setAttr ".rsrr" -type "double3" -1.3138424123623718e-15 -4.8612945760015501e-15 -1.8853483316878462e-14 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:RingFinger2_R_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000721";
	addAttr -ci true -k true -sn "w0" -ln "FKXRingFinger2_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -21.743351280297933 68.058276689401566 3.73683828210932 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 80.451307395432096 -7.1897075339205676 -45.184839106355533 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999956 0.99999999999999967 0.99999999999999978 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" -47.597736897333014 -17.703249453833084 -18.404353966845175 ;
	setAttr ".rst" -type "double3" 2.5823924595557628 -7.1054273576010019e-15 -1.0325074129013956e-14 ;
	setAttr ".rsrr" -type "double3" -1.7868878010214465e-14 9.5280267173414284e-15 -3.1805546814635152e-15 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:RingFinger1_R_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000722";
	addAttr -ci true -k true -sn "w0" -ln "FKXRingFinger1_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -22.586851034915572 70.452492125846334 3.2625056741009031 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 84.734799274962398 -10.584155284416987 -70.592263272819537 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999944 0.99999999999999978 0.99999999999999978 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" -55.298501438203651 -25.561148204022555 -13.939365216677528 ;
	setAttr ".rst" -type "double3" 5.5468274631967702 -0.87121337525205433 0.085476270302692114 ;
	setAttr ".rsrr" -type "double3" 1.4445198033228217e-30 1.1728295387896722e-14 -1.4113711398994355e-14 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:Cup_R_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000723";
	addAttr -ci true -k true -sn "w0" -ln "FKXCup_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -21.721479679055278 75.809248357339229 1.8168539396588448 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 85.778524604137147 -23.762614689202291 -97.599241183507019 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999956 0.99999999999999978 0.99999999999999989 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" -12.729940650397234 1.0619713053672607e-10 99.22996560434251 ;
	setAttr ".rst" -type "double3" 2.5323556682531603 -1.7906199654992676 0.353309122702548 ;
	setAttr ".rsrr" -type "double3" -2.4848083448933661e-16 6.7804207711277884e-15 9.5269104948427452e-15 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:ThumbFinger3_R_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000724";
	addAttr -ci true -k true -sn "w0" -ln "FKXThumbFinger3_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -18.090824298283167 71.275309601201997 6.9948290692322814 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -12.91869952414846 -22.173578972464881 -81.446431961489623 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999978 0.99999999999999956 0.99999999999999989 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" -135.00000000185091 0 0 ;
	setAttr ".rst" -type "double3" 2.150473604284997 -1.0658141036401503e-14 -1.0658141036401503e-14 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:ThumbFinger2_R_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000725";
	addAttr -ci true -k true -sn "w0" -ln "FKXThumbFinger2_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -18.387018382391425 73.244594077568564 6.1832106623392509 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -12.91869952414846 -22.173578972464881 -81.446431961489623 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999978 0.99999999999999956 0.99999999999999989 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 132.02207190553278 13.192708709780668 8.4913707547443735 ;
	setAttr ".rst" -type "double3" 4.0601659831538512 3.5527136788005009e-15 7.1054273576010019e-14 ;
	setAttr ".rsrr" -type "double3" 2.5444437451708147e-14 -2.0748149679859654e-14 3.6079417167851773e-14 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:ThumbFinger1_R_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000726";
	addAttr -ci true -k true -sn "w0" -ln "FKXThumbFinger1_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -19.374592791099694 76.387260344074704 3.8097546725663869 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -19.257161348515769 -35.772701098256043 -72.55481439004032 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999978 0.99999999999999967 0.99999999999999978 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 80.159712481810118 -60.562589243841643 76.544934276002124 ;
	setAttr ".rst" -type "double3" 3.0055150379940798 0.51952218981556086 -1.7089693953339626 ;
	setAttr ".rsrr" -type "double3" 1.133072605271378e-14 -1.7493050748049341e-14 9.5416640443905519e-15 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:NeckPart2_M_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000072C";
	addAttr -ci true -k true -sn "w0" -ln "FKXNeckPart2_MW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -4.3918006181386016e-14 135.32647068761261 -2.2280762541289505 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 89.999999999999972 -17.009868441056707 89.999999999999986 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999978 0.99999999999999989 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 1.2444419780077709 -2.1316282072803006e-14 -9.1198416419172349e-15 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:NeckPart1_M_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000072D";
	addAttr -ci true -k true -sn "w0" -ln "FKXNeckPart1_MW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -3.5415217239239953e-14 134.13646758974349 -2.5921208443781993 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 89.999999999999972 -17.009868441056707 89.999999999999986 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999978 0.99999999999999989 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 1.2444419780076856 7.1054273576010019e-14 -6.8047877108372696e-15 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:Chest_M_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000072F";
	addAttr -ci true -k true -sn "w0" -ln "FKXChest_MW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -8.7544107833280146e-14 122.64276660148766 -2.436565956867855 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 89.999999999999972 2.8868916598520848 89.999999999999986 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999978 0.99999999999999989 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 0 0 5.2479152244148028e-14 ;
	setAttr ".rst" -type "double3" 12.624062549953052 7.1054273576010019e-15 -5.5814327926330206e-14 ;
	setAttr ".rsrr" -type "double3" 0 0 2.7034714792439894e-14 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:Spine2_M_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000731";
	addAttr -ci true -k true -sn "w0" -ln "FKXSpine2_MW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -5.6412702975860404e-14 110.21566086761975 -0.21530542635936667 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 89.999999999999972 10.134208501402135 89.999999999999972 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999978 0.99999999999999989 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 0 0 3.3395824155366928e-14 ;
	setAttr ".rst" -type "double3" 11.252214457917376 1.7763568394002505e-15 -4.1386492997657091e-14 ;
	setAttr ".rsrr" -type "double3" 0 0 1.5107634736951704e-14 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:Spine1_M_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000732";
	addAttr -ci true -k true -sn "w0" -ln "FKXSpine1_MW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -2.5048665071004573e-14 99.00785063641176 0.78335368875192013 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 89.999999999999972 5.0918278134747581 89.999999999999986 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999967 0.99999999999999978 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 0 0 3.3395824155366915e-14 ;
	setAttr ".rst" -type "double3" 3.3816508661515456 -3.1086244689504383e-15 -2.0743979960866849e-14 ;
	setAttr ".rsrr" -type "double3" 0 0 1.5107634736951704e-14 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:RootPart2_M_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000733";
	addAttr -ci true -k true -sn "w0" -ln "FKXRootPart2_MW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -7.3081944324139563e-15 95.62777956513743 0.67999928063213388 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 89.999999999999972 -1.7514208112243506 89.999999999999986 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999978 0.99999999999999978 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 3.3816508661518299 2.2204460492503131e-15 -7.5403910957633823e-15 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:RootPart1_M_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000734";
	addAttr -ci true -k true -sn "w0" -ln "FKXRootPart1_MW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -8.9411933250420359e-16 92.247708493862774 0.57664487251233087 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 89.999999999999972 -1.7514208112243506 89.999999999999986 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999978 0.99999999999999978 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 3.3816508661516451 -4.4408920985006262e-15 -3.7860044429180047e-15 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:Root_M_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000735";
	addAttr -ci true -k true -sn "w0" -ln "FKXRoot_MW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 1.7655691145602508e-15 88.867637422588331 0.47329046439254197 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 89.999999999999972 -1.7514208112243506 89.999999999999986 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999978 0.99999999999999978 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 1.7655691145602508e-15 88.867637422588331 0.47329046439254197 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:Ankle_L_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000737";
	addAttr -ci true -k true -sn "w0" -ln "FKXAnkle_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 4.3081967054321879 7.3707391755913818 -5.6101808417092975 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -78.990415584663666 -2.1617832600572345e-13 89.999999999999375 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999989 1 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" -4.0303591354170538e-14 -1.2771914892752053e-14 -3.4928950904166135e-13 ;
	setAttr ".rst" -type "double3" -37.335576807430016 -1.7763568394002505e-15 -1.7763568394002505e-15 ;
	setAttr ".rsrr" -type "double3" -4.2738703532166128e-15 1.1479814553407384e-14 1.3678869938638011e-13 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:Knee_L_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000738";
	addAttr -ci true -k true -sn "w0" -ln "FKXKnee_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 6.7944379482859638 44.360948606597539 -1.1956246606031888 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -84.903524596727252 -6.7905351051608367 86.154733999028068 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999989 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 0 0 -8.746525374024671e-14 ;
	setAttr ".rst" -type "double3" -12.43903387975913 -6.6835426082434424e-14 2.6911806116913795e-13 ;
	setAttr ".rsrr" -type "double3" 0 0 -2.0673605429512861e-14 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:Wrist_L_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000074A";
	addAttr -ci true -k true -sn "w0" -ln "FKXWrist_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 20.987722480873316 78.841785267579098 1.9132525377467489 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -96.43781231576304 32.690834179111739 93.414234120871797 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999989 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" -8.6727576262856526e-14 -5.0590697902029e-14 -8.3516349728385731e-14 ;
	setAttr ".rst" -type "double3" -7.5870240637033106 -9.9475983006414026e-14 -2.6290081223123707e-13 ;
	setAttr ".rsrr" -type "double3" -3.5591773530166441e-14 2.8823776800763339e-15 -7.0047135493848062e-14 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:Scapula_L_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000074B";
	addAttr -ci true -k true -sn "w0" -ln "FKXScapula_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 1.1096741025741261 127.62381171178185 0.74229571841644049 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 85.356850077671339 203.35018097290126 2.2698015910307854 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 1 0.99999999999999989 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 3.1805546814635357e-15 3.1805546814635168e-14 -6.6791648310733855e-14 ;
	setAttr ".rst" -type "double3" 4.8146220815627601 3.4256949883352341 1.1096741025742134 ;
	setAttr ".rsrr" -type "double3" -2.2263882770244624e-14 1.2976884516267474e-29 -6.6791648310733881e-14 ;
	setAttr -k on ".w0";
createNode parentConstraint -n "rig:Breast_L_parentConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000074C";
	addAttr -ci true -k true -sn "w0" -ln "FKXBreast_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 6.6289249529644723 118.6863431191844 6.3461121142701282 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -50.049352591631994 42.141771766787443 118.76944248815805 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999989 1 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" -5.7249984266343308e-14 -1.9083328088781094e-14 1.2722218725854075e-14 ;
	setAttr ".rst" -type "double3" 7.1840143228174185 7.9495028875400102 6.6289249529645291 ;
	setAttr ".rsrr" -type "double3" -3.8961794847928075e-14 -9.5416640443905408e-15 2.5444437451708134e-14 ;
	setAttr -k on ".w0";
createNode pointConstraint -n "rig:Hip_R_pointConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000074D";
	addAttr -ci true -k true -sn "w0" -ln "FKXHip_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -8.8414397624647645 81.615172853450829 -1.9017649399230727 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 95.061538946391451 -1.0842554986393171 -86.854940697119858 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999978 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -7.3216659883418487 -2.1522866108679573 -8.8414397624647592 ;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:Hip_R_orientConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000074E";
	addAttr -ci true -k true -sn "w0" -ln "TwisterHip0_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -8.8414397624647645 81.615172853450829 -1.9017649399230727 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 95.061538946391451 -1.0842554986393171 -86.854940697119858 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999978 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 0 1.1927080055488188e-15 0 ;
	setAttr ".rsrr" -type "double3" -1.4655548255244661e-33 -4.2241741863187325e-16 -3.975693351829395e-16 ;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:HipPart1_R_orientConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000074F";
	addAttr -ci true -k true -sn "w0" -ln "TwisterHip1_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -8.1591058244052377 69.197098104499759 -1.6663848468164659 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 95.061538946391451 -1.0842554986393171 -86.854940697119858 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999978 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:HipPart2_R_orientConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000750";
	addAttr -ci true -k true -sn "w0" -ln "TwisterHip2_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -7.4767718863457153 56.779023355548574 -1.4310047537098609 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 95.061538946391451 -1.0842554986393171 -86.854940697119858 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999978 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:Elbow_R_orientConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000752";
	addAttr -ci true -k true -sn "w0" -ln "TwisterElbow0_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -19.053223849809214 99.96421895926278 -6.3430733567270119 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 79.590780110652801 -21.268495760848527 -95.232837323714676 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999956 0.99999999999999989 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" -27.306648488546891 28.455486590811169 52.109777568070434 ;
	setAttr ".rsrr" -type "double3" 0 0 -9.5416640443905503e-15 ;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:ElbowPart1_R_orientConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000753";
	addAttr -ci true -k true -sn "w0" -ln "TwisterElbow1_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -19.698056726830419 92.923407728701548 -3.590964725235843 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 79.590780110652801 -21.268495760848527 -95.232837323714676 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999956 0.99999999999999989 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:ElbowPart2_R_orientConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000754";
	addAttr -ci true -k true -sn "w0" -ln "TwisterElbow2_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -20.342889603851585 85.882596498140174 -0.83885609374462433 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 79.590780110652801 -21.268495760848527 -95.232837323714676 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999956 0.99999999999999989 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:Shoulder_R_orientConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000756";
	addAttr -ci true -k true -sn "w0" -ln "TwisterShoulder0_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -14.32897626712335 128.14777525332582 -4.9690466428544493 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 80.295538077017426 2.7527732444792115 -99.515696727980583 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999967 0.99999999999999989 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" -85.306801775312977 -0.60180005419151328 118.67873299758395 ;
	setAttr ".rsrr" -type "double3" 6.3611093629270335e-15 7.1562480332929135e-15 -3.9725156682451432e-31 ;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:ShoulderPart1_R_orientConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000757";
	addAttr -ci true -k true -sn "w0" -ln "TwisterShoulder1_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -15.90372546135198 118.75325648863809 -5.4270555474786235 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 80.295538077017426 2.7527732444792115 -99.515696727980583 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999967 0.99999999999999989 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:ShoulderPart2_R_orientConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000758";
	addAttr -ci true -k true -sn "w0" -ln "TwisterShoulder2_RW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -17.478474655580662 109.35873772395047 -5.8850644521027782 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 80.295538077017426 2.7527732444792115 -99.515696727980583 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999967 0.99999999999999989 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode pointConstraint -n "rig:Hip_L_pointConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000759";
	addAttr -ci true -k true -sn "w0" -ln "FKXHip_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 8.8414397624647396 81.615172853450829 -1.9017649399230727 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -84.938461053608592 1.084255498639219 86.854940697119957 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999989 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -7.3216659883418629 -2.1522866108679661 8.8414397624647449 ;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:Hip_L_orientConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000075A";
	addAttr -ci true -k true -sn "w0" -ln "TwisterHip0_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 8.8414397624647396 81.615172853450829 -1.9017649399230727 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -84.938461053608592 1.084255498639219 86.854940697119957 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999989 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" -5.5173828725626996e-33 -7.9513867036587919e-16 -7.9513867036587919e-16 ;
	setAttr ".rsrr" -type "double3" 1.2424041724466862e-17 3.975693351829396e-16 4.310455369189608e-35 ;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:HipPart1_L_orientConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000075B";
	addAttr -ci true -k true -sn "w0" -ln "TwisterHip1_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 8.1591058244052324 69.19709810449973 -1.6663848468164737 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -84.938461053608592 1.084255498639219 86.854940697119957 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999989 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:HipPart2_L_orientConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000075C";
	addAttr -ci true -k true -sn "w0" -ln "TwisterHip2_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 7.4767718863457215 56.779023355548603 -1.4310047537098762 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -84.938461053608592 1.084255498639219 86.854940697119957 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999989 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode pointConstraint -n "rig:Elbow_L_pointConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000075D";
	addAttr -ci true -k true -sn "w0" -ln "FKXElbow_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 19.053223849809399 99.964218959263007 -6.3430733567268955 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -100.40921988934704 21.268495760848392 95.232837323715032 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999978 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -9.5365916922528555 -2.1528047753349711e-06 4.9737991503207013e-14 ;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:Elbow_L_orientConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000075E";
	addAttr -ci true -k true -sn "w0" -ln "TwisterElbow0_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 19.053223849809399 99.964218959263007 -6.3430733567268955 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -100.40921988934704 21.268495760848392 95.232837323715032 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999978 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" 0 0 5.4069429584879788e-14 ;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:ElbowPart1_L_orientConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000075F";
	addAttr -ci true -k true -sn "w0" -ln "TwisterElbow1_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 19.698056726830622 92.923407728701605 -3.590964725235736 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -100.40921988934704 21.268495760848392 95.232837323715032 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999978 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:ElbowPart2_L_orientConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000760";
	addAttr -ci true -k true -sn "w0" -ln "TwisterElbow2_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 20.342889603851855 85.882596498140273 -0.83885609374454662 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -100.40921988934704 21.268495760848392 95.232837323715032 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999978 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode pointConstraint -n "rig:Shoulder_L_pointConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000761";
	addAttr -ci true -k true -sn "w0" -ln "FKXShoulder_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 14.328976267123252 128.14777525332596 -4.9690466428543738 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -99.704461922982446 -2.7527732444791351 99.515696727980824 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999989 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -14.409854929115944 -7.1054273576010019e-15 -4.4053649617126212e-13 ;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:Shoulder_L_orientConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000762";
	addAttr -ci true -k true -sn "w0" -ln "TwisterShoulder0_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 14.328976267123252 128.14777525332596 -4.9690466428543738 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -99.704461922982446 -2.7527732444791351 99.515696727980824 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999989 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".lr" -type "double3" -4.2937488199757468e-13 4.055207218865957e-14 7.1562480332929249e-14 ;
	setAttr ".rsrr" -type "double3" -1.2722218725854067e-14 1.2722218725854067e-14 3.1805546814635183e-15 ;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:ShoulderPart1_L_orientConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000763";
	addAttr -ci true -k true -sn "w0" -ln "TwisterShoulder1_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 15.903725461351998 118.75325648863826 -5.4270555474785365 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -99.704461922982446 -2.7527732444791351 99.515696727980824 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999989 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode orientConstraint -n "rig:ShoulderPart2_L_orientConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000764";
	addAttr -ci true -k true -sn "w0" -ln "TwisterShoulder2_LW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 17.478474655580762 109.35873772395065 -5.885064452102684 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -99.704461922982446 -2.7527732444791351 99.515696727980824 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999989 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -k on ".w0";
createNode pointConstraint -n "rig:HipPart1_R_pointConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000765";
	addAttr -ci true -k true -sn "w0" -ln "FKIKMixKnee_RW0" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "w1" -ln "Hip_RW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -7.8179388553753473 62.988060730024173 -1.5486948002631336 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 95.061538946391451 -1.0842554986393171 -86.854940697119858 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999978 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr ".rst" -type "double3" 18.658550819638712 1.577210584358113e-14 -1.3677947663381929e-13 ;
	setAttr -k on ".w0" 0.33333333333333331;
	setAttr -k on ".w1" 0.66666666666666674;
createNode pointConstraint -n "rig:HipPart2_R_pointConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000766";
	addAttr -ci true -k true -sn "w0" -ln "FKIKMixKnee_RW0" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "w1" -ln "Hip_RW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -7.8179388553753499 62.988060730024173 -1.5486948002631338 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 95.061538946391451 -1.0842554986393171 -86.854940697119858 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999978 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr ".rst" -type "double3" 6.2195169398795898 5.3360094121046586e-15 -4.5297099404706387e-14 ;
	setAttr -k on ".w0" 0.66666666666666663;
	setAttr -k on ".w1" 0.33333333333333337;
createNode pointConstraint -n "rig:ElbowPart1_R_pointConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000767";
	addAttr -ci true -k true -sn "w1" -ln "Elbow_RW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -20.020473165341151 89.403002113420797 -2.2149104094901899 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 79.590780110652801 -21.268495760848527 -95.232837323714676 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999956 0.99999999999999989 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 11.380536095555101 7.1054273576010019e-15 1.6342482922482304e-13 ;
	setAttr -k on ".w1" 0.66666666666666674;
createNode pointConstraint -n "rig:ElbowPart2_R_pointConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000768";
	addAttr -ci true -k true -sn "w1" -ln "Elbow_RW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -20.020473165341155 89.403002113420783 -2.2149104094901846 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 79.590780110652801 -21.268495760848527 -95.232837323714676 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999956 0.99999999999999989 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 3.7935120318517477 0 4.9737991503207013e-14 ;
	setAttr -k on ".w1" 0.33333333333333337;
createNode pointConstraint -n "rig:ShoulderPart1_R_pointConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000769";
	addAttr -ci true -k true -sn "w1" -ln "Shoulder_RW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -16.69110005846629 114.0559971062943 -5.6560599997907266 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 80.295538077017426 2.7527732444792115 -99.515696727980583 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999967 0.99999999999999989 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 14.304888238060173 0 -9.9475983006414026e-14 ;
	setAttr -k on ".w1" 0.66666666666666674;
createNode pointConstraint -n "rig:ShoulderPart2_R_pointConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000076A";
	addAttr -ci true -k true -sn "w1" -ln "Shoulder_RW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" -16.691100058466287 114.0559971062943 -5.656059999790731 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" 80.295538077017426 2.7527732444792115 -99.515696727980583 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999967 0.99999999999999989 1 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 4.768296079353405 -3.5527136788005009e-15 -3.5527136788005009e-14 ;
	setAttr -k on ".w1" 0.33333333333333337;
createNode pointConstraint -n "rig:HipPart1_L_pointConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000076B";
	addAttr -ci true -k true -sn "w0" -ln "FKIKMixKnee_LW0" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "w1" -ln "Hip_LW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 7.8179388553753464 62.988060730024173 -1.5486948002631351 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -84.938461053608592 1.084255498639219 86.854940697119957 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999989 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr ".rst" -type "double3" -18.658550819638712 -4.5741188614556449e-14 1.4210854715202004e-13 ;
	setAttr -k on ".w0" 0.33333333333333331;
	setAttr -k on ".w1" 0.66666666666666674;
createNode pointConstraint -n "rig:HipPart2_L_pointConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000076C";
	addAttr -ci true -k true -sn "w0" -ln "FKIKMixKnee_LW0" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "w1" -ln "Hip_LW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 7.8179388553753482 62.988060730024188 -1.5486948002631358 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -84.938461053608592 1.084255498639219 86.854940697119957 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999989 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr ".rst" -type "double3" -6.2195169398795755 -1.5099033134902129e-14 4.4408920985006262e-14 ;
	setAttr -k on ".w0" 0.66666666666666663;
	setAttr -k on ".w1" 0.33333333333333337;
createNode pointConstraint -n "rig:ElbowPart1_L_pointConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000076D";
	addAttr -ci true -k true -sn "w0" -ln "FKIKMixWrist_LW0" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "w1" -ln "Elbow_LW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 20.020473165341361 89.403002113421039 -2.2149104094900789 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -100.40921988934704 21.268495760848392 95.232837323715032 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999978 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr ".rst" -type "double3" -11.380536095555087 -3.907985046680551e-14 -1.2789769243681803e-13 ;
	setAttr -k on ".w0" 0.33333333333333331;
	setAttr -k on ".w1" 0.66666666666666674;
createNode pointConstraint -n "rig:ElbowPart2_L_pointConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000076E";
	addAttr -ci true -k true -sn "w0" -ln "FKIKMixWrist_LW0" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "w1" -ln "Elbow_LW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 20.020473165341354 89.403002113421039 -2.2149104094900731 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -100.40921988934704 21.268495760848392 95.232837323715032 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 1 0.99999999999999978 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr ".rst" -type "double3" -3.793512031851705 -1.7763568394002505e-14 -3.5527136788005009e-14 ;
	setAttr -k on ".w0" 0.66666666666666663;
	setAttr -k on ".w1" 0.33333333333333337;
createNode pointConstraint -n "rig:ShoulderPart1_L_pointConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000076F";
	addAttr -ci true -k true -sn "w0" -ln "FKIKMixElbow_LW0" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "w1" -ln "Shoulder_LW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 16.691100058466326 114.05599710629448 -5.6560599997906378 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -99.704461922982446 -2.7527732444791351 99.515696727980824 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999989 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr ".rst" -type "double3" -14.304888238060158 1.7763568394002505e-14 2.8421709430404007e-14 ;
	setAttr -k on ".w0" 0.33333333333333331;
	setAttr -k on ".w1" 0.66666666666666674;
createNode pointConstraint -n "rig:ShoulderPart2_L_pointConstraint1" -p "rig:ConstraintSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000770";
	addAttr -ci true -k true -sn "w0" -ln "FKIKMixElbow_LW0" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "w1" -ln "Shoulder_LW1" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr ".t" -type "double3" 16.691100058466322 114.05599710629448 -5.6560599997906342 ;
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr ".r" -type "double3" -99.704461922982446 -2.7527732444791351 99.515696727980824 ;
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999989 1.0000000000000002 ;
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr -s 2 ".tg";
	setAttr ".rst" -type "double3" -4.768296079353405 3.5527136788005009e-15 1.4210854715202004e-14 ;
	setAttr -k on ".w0" 0.66666666666666663;
	setAttr -k on ".w1" 0.33333333333333337;
createNode transform -n "rig:DeformationSystem" -p "rig:Main";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000779";
createNode joint -n "rig:Root_M" -p "rig:DeformationSystem";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000077A";
	addAttr -ci true -sn "fat" -ln "fat" -dv 15.228545711992602 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 0.64999999999999991 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 89.999999999999972 -1.7514208112243506 89.999999999999986 ;
	setAttr ".bps" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -5.8064397712757788e-15 88.867637422588331 0.47329046439253208 1;
	setAttr ".ds" 2;
createNode joint -n "rig:Hip_R" -p "rig:Root_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000077B";
	addAttr -ci true -sn "fat" -ln "fat" -dv 7.7934322173138595 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -k true -sn "twistAmount" -ln "twistAmount" -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "twistAddition" -ln "twistAddition" -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -174.87888821990936 -3.1444956129666579 177.16268854732138 ;
	setAttr ".ds" 2;
	setAttr -k on ".twistAmount";
	setAttr -k on ".twistAddition";
createNode joint -n "rig:HipPart1_R" -p "rig:Hip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000077C";
	addAttr -ci true -k true -sn "twistAmount" -ln "twistAmount" -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "twistAddition" -ln "twistAddition" -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
	setAttr -k on ".twistAmount" 0.33333333333333331;
	setAttr -k on ".twistAddition";
createNode joint -n "rig:HipPart2_R" -p "rig:HipPart1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000077D";
	addAttr -ci true -k true -sn "twistAmount" -ln "twistAmount" -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "twistAddition" -ln "twistAddition" -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
	setAttr -k on ".twistAmount" 0.66666666666666663;
	setAttr -k on ".twistAddition";
createNode joint -n "rig:Knee_R" -p "rig:HipPart2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000077E";
	addAttr -ci true -sn "fat" -ln "fat" -dv 5.3747808395268004 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 -7.9057337300925665 ;
	setAttr ".ds" 2;
createNode joint -n "rig:Ankle_R" -p "rig:Knee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000077F";
	addAttr -ci true -sn "fat" -ln "fat" -dv 3.3144481843748594 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 3;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 5.9408887441646741 -3.2284396665911013 7.1034334747240271 ;
	setAttr ".ds" 2;
createNode joint -n "rig:Toes_R" -p "rig:Ankle_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000780";
	addAttr -ci true -sn "fat" -ln "fat" -dv 2.6873904197633998 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 5.724997006951539 11.847151218614583 1.1990408665951691e-13 ;
	setAttr ".r" -type "double3" 9.4979314175203866e-13 1.2225257056878435e-13 3.6688257332559259e-12 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -0.79120452720448853 -3.8922531593420087 75.808229210289667 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:ToesEnd_R" -p "rig:Toes_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000781";
	addAttr -ci true -sn "fat" -ln "fat" -dv 2.6873904197633998 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	setAttr ".t" -type "double3" 6.5710341663822938 -1.3322676295501878e-15 -1.4210854715202004e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:HipFat1_R" -p "rig:Hip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000782";
	addAttr -ci true -sn "fat" -ln "fat" -dv 8.7444355155545352 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -1.6148669790486991 -4.9370587667259098 0.5595644810493674 ;
	setAttr ".r" -type "double3" -1.431249606658583e-14 -7.9513867036587856e-15 6.3611093629270335e-14 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 173.73512402025605 10.018203319904885 -47.898367133145562 ;
	setAttr ".ds" 2;
createNode joint -n "rig:HipFatEnd_R" -p "rig:HipFat1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000783";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	setAttr ".t" -type "double3" 8.7444355155543079 2.5579538487363607e-13 7.2830630415410269e-14 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:RootPart1_M" -p "rig:Root_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000784";
	addAttr -ci true -sn "fat" -ln "fat" -dv 15.228545711992602 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 0.64999999999999991 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -8.4661282183402214e-15 92.247708493862774 0.57664487251232144 1;
	setAttr ".ds" 2;
createNode joint -n "rig:RootPart2_M" -p "rig:RootPart1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000785";
	addAttr -ci true -sn "fat" -ln "fat" -dv 15.228545711992602 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 0.64999999999999991 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -1.4880203318249975e-14 95.62777956513743 0.679999280632124 1;
	setAttr ".ds" 2;
createNode joint -n "rig:Spine1_M" -p "rig:RootPart2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000786";
	addAttr -ci true -sn "fat" -ln "fat" -dv 15.228545711992602 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 0.64999999999999991 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 -6.8432486246991227 ;
	setAttr ".bps" -type "matrix" 3.9022319828289058e-16 0.99605373441152578 -0.088752229069772759 0 -4.5635506035450333e-16 0.088752229069772801 0.99605373441152578 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -3.2620673956840621e-14 99.00785063641176 0.78335368875191036 1;
	setAttr ".ds" 2;
createNode joint -n "rig:Spine2_M" -p "rig:Spine1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000787";
	addAttr -ci true -sn "fat" -ln "fat" -dv 15.228545711992602 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 0.64999999999999991 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 -5.042380687927376 ;
	setAttr ".bps" -type "matrix" 4.2882324480567283e-16 0.9843983016318395 -0.17595449339062053 0 -4.2029122082625572e-16 0.17595449339062058 0.9843983016318395 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -6.3984711861696432e-14 110.21566086761975 -0.21530542635938044 1;
	setAttr ".ds" 2;
createNode joint -n "rig:Chest_M" -p "rig:Spine2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000788";
	addAttr -ci true -sn "fat" -ln "fat" -dv 15.228545711992602 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 0.64999999999999991 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 7.2473168415500497 ;
	setAttr ".bps" -type "matrix" 3.7237652132655553e-16 0.9987309058863858 -0.05036444804978249 0 -4.7103058494541928e-16 0.050364448049782545 0.99873090588638569 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -9.511611671911613e-14 122.64276660148768 -2.4365659568678684 1;
	setAttr ".ds" 2;
createNode joint -n "rig:Scapula_R" -p "rig:Chest_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000789";
	addAttr -ci true -sn "fat" -ln "fat" -dv 5.8226792428207004 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 4.8146220815627174 3.4256949883352332 -1.1096741025741679 ;
	setAttr ".r" -type "double3" -4.9298597562684496e-14 1.4710065401768792e-14 -6.6791648310733881e-14 ;
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -88.932374518838401 66.545906828885009 -81.871415947736608 ;
	setAttr ".ds" 2;
createNode joint -n "rig:Shoulder_R" -p "rig:Scapula_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000078A";
	addAttr -ci true -sn "fat" -ln "fat" -dv 5.8226792428207004 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -k true -sn "twistAmount" -ln "twistAmount" -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "twistAddition" -ln "twistAddition" -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 14.409854929115934 -4.9737991503207013e-14 3.4106051316484809e-13 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -1.9899710554437907e-14 80.803017877340949 32.56595464522421 ;
	setAttr ".ds" 2;
	setAttr -k on ".twistAmount";
	setAttr -k on ".twistAddition";
createNode joint -n "rig:ShoulderPart1_R" -p "rig:Shoulder_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000078B";
	addAttr -ci true -k true -sn "twistAmount" -ln "twistAmount" -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "twistAddition" -ln "twistAddition" -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
	setAttr -k on ".twistAmount" 0.33333333333333331;
	setAttr -k on ".twistAddition";
createNode joint -n "rig:ShoulderPart2_R" -p "rig:ShoulderPart1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000078C";
	addAttr -ci true -k true -sn "twistAmount" -ln "twistAmount" -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "twistAddition" -ln "twistAddition" -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
	setAttr -k on ".twistAmount" 0.66666666666666663;
	setAttr -k on ".twistAddition";
createNode joint -n "rig:Elbow_R" -p "rig:ShoulderPart2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000078D";
	addAttr -ci true -sn "fat" -ln "fat" -dv 4.0310856296450988 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -k true -sn "twistAmount" -ln "twistAmount" -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "twistAddition" -ln "twistAddition" -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 9.5365916922529124 2.1528047682295437e-06 -1.4210854715202004e-13 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 24.384535906822897 ;
	setAttr ".ds" 2;
	setAttr -k on ".twistAmount";
	setAttr -k on ".twistAddition";
createNode joint -n "rig:ElbowPart1_R" -p "rig:Elbow_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000078E";
	addAttr -ci true -k true -sn "twistAmount" -ln "twistAmount" -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "twistAddition" -ln "twistAddition" -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
	setAttr -k on ".twistAmount" 0.33333333333333331;
	setAttr -k on ".twistAddition";
createNode joint -n "rig:ElbowPart2_R" -p "rig:ElbowPart1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000078F";
	addAttr -ci true -k true -sn "twistAmount" -ln "twistAmount" -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "twistAddition" -ln "twistAddition" -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
	setAttr -k on ".twistAmount" 0.66666666666666663;
	setAttr -k on ".twistAddition";
createNode joint -n "rig:Wrist_R" -p "rig:ElbowPart2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000790";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.5228545711992589 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 2.3100000000000005 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 7.5870240637034954 -2.4868995751603507e-14 2.9842794901924208e-13 ;
	setAttr ".r" -type "double3" -1.5130929815185071e-14 4.0253895187272642e-14 -2.5487145095135985e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 4.7454770241091335 -0.54662596273651254 11.5232860986058 ;
	setAttr ".ds" 2;
createNode joint -n "rig:IndexFinger1_R" -p "rig:Wrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000791";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -17.978446422947293 16.900243142536748 -13.960823264685583 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:IndexFinger2_R" -p "rig:IndexFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000792";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0.010485631963580424 27.008834952951645 0.023033164457426328 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:IndexFinger3_R" -p "rig:IndexFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000793";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -1.6442876069197914 5.8054592845604764 -0.23435582923541479 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:IndexFinger4_R" -p "rig:IndexFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000794";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	setAttr ".t" -type "double3" 2.1624510102975236 -1.4210854715202004e-14 4.2632564145606011e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:MiddleFinger1_R" -p "rig:Wrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000795";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -6.1747855731786805 25.426212501972994 -16.197120816641625 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:MiddleFinger2_R" -p "rig:MiddleFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000796";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0.045986292016828877 26.091137027921068 -1.9069852353626116 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:MiddleFinger3_R" -p "rig:MiddleFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000797";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0.055293955366047622 15.097605855418335 0.015733628781366145 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:MiddleFinger4_R" -p "rig:MiddleFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000798";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	setAttr ".t" -type "double3" 2.4045706881762925 -1.4210854715202004e-14 -2.8421709430404007e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:Cup_R" -p "rig:Wrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000799";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053599 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0.45785549513176471 -2.8152498444385938 -9.2412163815406583 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:PinkyFinger1_R" -p "rig:Cup_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000079A";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 22.617847931619039 22.742350339945716 -15.943479074518994 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:PinkyFinger2_R" -p "rig:PinkyFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000079B";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0.26854292613979497 23.335859002795008 0.031032081073231712 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:PinkyFinger3_R" -p "rig:PinkyFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000079C";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 2.2995238920477661 20.979648262889942 0.79713441173641131 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:PinkyFinger4_R" -p "rig:PinkyFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000079D";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	setAttr ".t" -type "double3" 1.5938321557453818 -7.1054273576010019e-14 8.5265128291212022e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:RingFinger1_R" -p "rig:Cup_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000079E";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 4.732524089104416 27.307436750159503 -9.8124795827448992 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:RingFinger2_R" -p "rig:RingFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B4240000079F";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -0.32607685844592477 25.321589444470568 -0.14867714781562358 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:RingFinger3_R" -p "rig:RingFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007A0";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0.57445180684387764 9.6423798917985444 0.10482938358205179 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:RingFinger4_R" -p "rig:RingFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007A1";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	setAttr ".t" -type "double3" 2.772419175806931 -6.7501559897209518e-14 0 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:ThumbFinger1_R" -p "rig:Wrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007A2";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -90.021643621060875 16.130702675840425 6.8369242914052011 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:ThumbFinger2_R" -p "rig:ThumbFinger1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007A3";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 1.5189199068329204 15.250338304898436 -3.5491471333837215 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:ThumbFinger3_R" -p "rig:ThumbFinger2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007A4";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:ThumbFinger4_R" -p "rig:ThumbFinger3_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007A5";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	setAttr ".t" -type "double3" 2.5380360186267552 -3.3073712693010293e-06 -2.1135456194087965e-06 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:Neck_M" -p "rig:Chest_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007A6";
	addAttr -ci true -sn "fat" -ln "fat" -dv 8.957968065878001 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 10.316790868949951 2.3980817331903381e-14 1.8836197044295709e-14 ;
	setAttr ".r" -type "double3" 0 0 1.2722218725854067e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 19.896760100908789 ;
	setAttr ".bps" -type "matrix" 1.89844254998307e-16 0.95625438461518619 0.29253641124521801 0 -5.6964308512737003e-16 -0.29253641124521795 0.95625438461518619 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -7.2438188979787272e-14 132.94646449187445 -2.9561654346275383 1;
	setAttr ".ds" 2;
createNode joint -n "rig:NeckPart1_M" -p "rig:Neck_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007A7";
	addAttr -ci true -sn "fat" -ln "fat" -dv 8.3110037055645911 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1.89844254998307e-16 0.95625438461518619 0.29253641124521801 0 -5.6964308512737003e-16 -0.29253641124521795 0.95625438461518619 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -7.8905728509652967e-14 134.13646758974349 -2.5921208443782149 1;
	setAttr ".ds" 2;
createNode joint -n "rig:NeckPart2_M" -p "rig:NeckPart1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007A8";
	addAttr -ci true -sn "fat" -ln "fat" -dv 7.6640393452511786 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1.89844254998307e-16 0.95625438461518619 0.29253641124521801 0 -5.6964308512737003e-16 -0.29253641124521795 0.95625438461518619 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -8.7722001872069275e-14 135.32647068761258 -2.2280762541289505 1;
	setAttr ".ds" 2;
createNode joint -n "rig:Neck1_M" -p "rig:NeckPart2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007A9";
	addAttr -ci true -sn "fat" -ln "fat" -dv 7.0170749849377678 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 1.2444419780078704 -1.4210854715202004e-14 -1.64283610131183e-14 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1.89844254998307e-16 0.95625438461518619 0.29253641124521801 0 -5.6964308512737003e-16 -0.29253641124521795 0.95625438461518619 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -1.031896704387601e-13 136.51647378548185 -1.8640316638796524 1;
	setAttr ".ds" 2;
createNode joint -n "rig:Neck2_M" -p "rig:Neck1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007AA";
	addAttr -ci true -sn "fat" -ln "fat" -dv 5.0761819039975338 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 3.7333259340233553 7.815970093361102e-14 -4.0239087725416945e-14 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1.89844254998307e-16 0.95625438461518619 0.29253641124521801 0 -5.6964308512737003e-16 -0.29253641124521795 0.95625438461518619 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -1.4288551599723397e-13 140.08648307908919 -0.77189789313170709 1;
	setAttr ".ds" 2;
createNode joint -n "rig:Head_M" -p "rig:Neck2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007AB";
	addAttr -ci true -sn "fat" -ln "fat" -dv 3.1352888230573002 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 3.7333259340227016 -2.1316282072803006e-14 -4.6854213441728523e-14 ;
	setAttr ".r" -type "double3" 0 0 -2.8624992133171654e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 -17.009868441056661 ;
	setAttr ".bps" -type "matrix" 3.4818074504994928e-16 0.99999999999999989 7.2164496600635175e-16 0 -4.8918734076604296e-16 -6.6613381477509392e-16 0.99999999999999989 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -1.8266580791981782e-13 143.65649237269599 0.3202358776159544 1;
	setAttr ".ds" 2;
createNode joint -n "rig:HeadEnd_M" -p "rig:Head_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007AC";
	addAttr -ci true -sn "fat" -ln "fat" -dv 3.1352888230573002 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	setAttr ".t" -type "double3" 17.362852582835643 -8.7763130096618625e-14 -9.7231318681485433e-14 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:Scapula_L" -p "rig:Chest_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007AD";
	addAttr -ci true -sn "fat" -ln "fat" -dv 5.8226792428207004 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -88.932374518837747 66.545906828885037 98.128584052263989 ;
	setAttr ".ds" 2;
createNode joint -n "rig:Shoulder_L" -p "rig:Scapula_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007AE";
	addAttr -ci true -sn "fat" -ln "fat" -dv 5.8226792428207004 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -k true -sn "twistAmount" -ln "twistAmount" -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "twistAddition" -ln "twistAddition" -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 80.803017877340892 32.565954645223911 ;
	setAttr ".ds" 2;
	setAttr -k on ".twistAmount";
	setAttr -k on ".twistAddition";
createNode joint -n "rig:ShoulderPart1_L" -p "rig:Shoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007AF";
	addAttr -ci true -k true -sn "twistAmount" -ln "twistAmount" -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "twistAddition" -ln "twistAddition" -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
	setAttr -k on ".twistAmount" 0.33333333333333331;
	setAttr -k on ".twistAddition";
createNode joint -n "rig:ShoulderPart2_L" -p "rig:ShoulderPart1_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007B0";
	addAttr -ci true -k true -sn "twistAmount" -ln "twistAmount" -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "twistAddition" -ln "twistAddition" -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
	setAttr -k on ".twistAmount" 0.66666666666666663;
	setAttr -k on ".twistAddition";
createNode joint -n "rig:Elbow_L" -p "rig:ShoulderPart2_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007B1";
	addAttr -ci true -sn "fat" -ln "fat" -dv 4.0310856296450988 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -k true -sn "twistAmount" -ln "twistAmount" -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "twistAddition" -ln "twistAddition" -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 24.384535906822681 ;
	setAttr ".ds" 2;
	setAttr -k on ".twistAmount";
	setAttr -k on ".twistAddition";
createNode joint -n "rig:ElbowPart1_L" -p "rig:Elbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007B2";
	addAttr -ci true -k true -sn "twistAmount" -ln "twistAmount" -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "twistAddition" -ln "twistAddition" -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
	setAttr -k on ".twistAmount" 0.33333333333333331;
	setAttr -k on ".twistAddition";
createNode joint -n "rig:ElbowPart2_L" -p "rig:ElbowPart1_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007B3";
	addAttr -ci true -k true -sn "twistAmount" -ln "twistAmount" -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "twistAddition" -ln "twistAddition" -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
	setAttr -k on ".twistAmount" 0.66666666666666663;
	setAttr -k on ".twistAddition";
createNode joint -n "rig:Wrist_L" -p "rig:ElbowPart2_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007B4";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.5228545711992589 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 2.3100000000000005 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 4.745477024109138 -0.54662596273651098 11.523286098605704 ;
	setAttr ".ds" 2;
createNode joint -n "rig:IndexFinger1_L" -p "rig:Wrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007B5";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -9.0507967385055537 -2.1316282072803006e-14 6.7501559897209518e-14 ;
	setAttr ".r" -type "double3" -7.3550327008843804e-15 8.5477407064331987e-15 1.5902773407317588e-15 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -17.97844642294729 16.900243142536734 -13.960823264685223 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:IndexFinger2_L" -p "rig:IndexFinger1_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007B6";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -2.6150711681150085 0 -4.9737991503207013e-14 ;
	setAttr ".r" -type "double3" -3.6650923087177233e-15 1.5903427917877486e-14 -1.0089874885482651e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0.01048563196355653 27.008834952951652 0.023033164457463121 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:IndexFinger3_L" -p "rig:IndexFinger2_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007B7";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -2.2798674841394728 5.6843418860808015e-14 5.5067062021407764e-14 ;
	setAttr ".r" -type "double3" 2.3694200573773864e-14 2.1889608513294971e-15 -3.8874826555856812e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -1.6442876069198151 5.8054592845604747 -0.23435582923541093 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:IndexFinger4_L" -p "rig:IndexFinger3_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007B8";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	setAttr ".t" -type "double3" -2.1624510102975378 3.907985046680551e-14 -5.6843418860808015e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:MiddleFinger1_L" -p "rig:Wrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007B9";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -8.7083736116588639 1.9121430819272476 -0.57542589341600703 ;
	setAttr ".r" -type "double3" 7.1562480332929182e-15 9.9392333795734856e-15 -7.1761265000520593e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -6.1747855731786672 25.426212501972945 -16.19712081664121 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:MiddleFinger2_L" -p "rig:MiddleFinger1_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007BA";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -2.929973576895506 -1.7763568394002505e-14 -9.7255536957163713e-14 ;
	setAttr ".r" -type "double3" 3.9160579515519557e-14 1.9426542241419486e-14 -3.2401900817409584e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0.045986292016820418 26.091137027921068 -1.9069852353625694 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:MiddleFinger3_L" -p "rig:MiddleFinger2_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007BB";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -2.3283439685010592 2.4868995751603507e-14 6.7501559897209518e-14 ;
	setAttr ".r" -type "double3" 7.2400326646722878e-14 -6.3939097733757849e-15 -5.1931717905663708e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0.055293955366036401 15.097605855418335 0.015733628781371075 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:MiddleFinger4_L" -p "rig:MiddleFinger3_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007BC";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	setAttr ".t" -type "double3" -2.4045706881764062 3.907985046680551e-14 1.4210854715202004e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:Cup_L" -p "rig:Wrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007BD";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053599 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -2.5323556682531816 1.7906199654992676 -0.35330912270257997 ;
	setAttr ".r" -type "double3" -8.4980445395353265e-15 -1.4293860003999125e-14 -2.9967565142021848e-14 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0.45785549513175416 -2.815249844438664 -9.2412163815403012 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:PinkyFinger1_L" -p "rig:Cup_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007BE";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -4.5250926779441443 2.3533218848592696 0.44446663353521387 ;
	setAttr ".r" -type "double3" 1.7095481412866407e-14 4.7708320221952657e-15 -6.1225677618172695e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 22.617847931619036 22.742350339945727 -15.943479074518953 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:PinkyFinger2_L" -p "rig:PinkyFinger1_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007BF";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -2.107538332853423 2.3092638912203256e-14 -7.9936057773011271e-15 ;
	setAttr ".r" -type "double3" 1.4132347461581056e-14 9.5803557133938036e-15 1.8847271296016236e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0.26854292613980946 23.335859002795008 0.031032081073182703 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:PinkyFinger3_L" -p "rig:PinkyFinger2_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007C0";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -1.5833293982736194 -5.3290705182007514e-14 1.5631940186722204e-13 ;
	setAttr ".r" -type "double3" 2.6935322458644153e-14 -4.5009973659920108e-14 -1.6598519743887716e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 2.2995238920477887 20.979648262889949 0.79713441173640109 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:PinkyFinger4_L" -p "rig:PinkyFinger3_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007C1";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	setAttr ".t" -type "double3" -1.5938321557451047 8.8817841970012523e-14 -1.4210854715202004e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:RingFinger1_L" -p "rig:Cup_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007C2";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -5.5468274631969336 0.87121337525208986 -0.085476270302692114 ;
	setAttr ".r" -type "double3" 1.3914926731402889e-14 8.2495637050459922e-15 -3.0811623476677818e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 4.7325240891044018 27.307436750159482 -9.8124795827448459 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:RingFinger2_L" -p "rig:RingFinger1_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007C3";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -2.5823924595557344 2.4868995751603507e-14 -2.5757174171303632e-14 ;
	setAttr ".r" -type "double3" 1.3427283093717565e-14 1.597040193131385e-14 -2.2599331896805227e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -0.32607685844591955 25.321589444470568 -0.1486771478156225 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:RingFinger3_L" -p "rig:RingFinger2_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007C4";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -2.2923824975698111 1.4210854715202004e-14 -1.7763568394002505e-13 ;
	setAttr ".r" -type "double3" 3.05142229778984e-14 3.0045409528451706e-14 -2.9451190907848706e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0.57445180684387875 9.6423798917985444 0.10482938358204859 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:RingFinger4_L" -p "rig:RingFinger3_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007C5";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	setAttr ".t" -type "double3" -2.7724191758068741 1.1723955140041653e-13 2.6290081223123707e-13 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:ThumbFinger1_L" -p "rig:Wrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007C6";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -3.0055150379941153 -0.51952218981555376 1.7089693953339413 ;
	setAttr ".r" -type "double3" 3.9756933518294788e-16 5.7249984266343308e-14 -1.6697912077683458e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -90.021643621060946 16.130702675840425 6.8369242914055395 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:ThumbFinger2_L" -p "rig:ThumbFinger1_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007C7";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -4.0601659831539507 5.3290705182007514e-15 7.815970093361102e-14 ;
	setAttr ".r" -type "double3" -1.4312496066585827e-14 2.8227422797988711e-14 -6.9574633657014084e-16 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 1.5189199068329313 15.250338304898436 -3.5491471333837183 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:ThumbFinger3_L" -p "rig:ThumbFinger2_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007C8";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -2.1504736042849117 6.3948846218409017e-14 -3.907985046680551e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:ThumbFinger4_L" -p "rig:ThumbFinger3_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007C9";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1.0749561679053592 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	setAttr ".t" -type "double3" -2.5380360186267481 3.3073712781828135e-06 2.1135456158560828e-06 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:Breast_R" -p "rig:Spine2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007CA";
	addAttr -ci true -sn "fat" -ln "fat" -dv 9.8468826655711581 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 7.1840143228173474 7.9495028875399996 -6.6289249529645149 ;
	setAttr ".r" -type "double3" 1.9083328088781101e-14 4.7708320221952783e-15 -1.9083328088781101e-14 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -160.27322953958824 20.907938333296205 144.22309514650735 ;
	setAttr ".ds" 2;
createNode joint -n "rig:BreastEnd_R" -p "rig:Breast_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007CB";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	setAttr ".t" -type "double3" 9.8468826655712931 1.4210854715202004e-14 -8.8817841970012523e-15 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:Breast_L" -p "rig:Spine2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007CC";
	addAttr -ci true -sn "fat" -ln "fat" -dv 9.8468826655711581 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -160.27322953958844 20.907938333296421 -35.776904853492766 ;
	setAttr ".ds" 2;
createNode joint -n "rig:BreastEnd_L" -p "rig:Breast_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007CD";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	setAttr ".t" -type "double3" -9.8468826655712931 9.9475983006414026e-14 5.2846615972157451e-14 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode joint -n "rig:Hip_L" -p "rig:Root_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007CE";
	addAttr -ci true -sn "fat" -ln "fat" -dv 7.7934322173138595 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -k true -sn "twistAmount" -ln "twistAmount" -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "twistAddition" -ln "twistAddition" -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -174.87888821990933 -3.144495612966554 -2.8373114526785574 ;
	setAttr ".ds" 2;
	setAttr -k on ".twistAmount";
	setAttr -k on ".twistAddition";
createNode joint -n "rig:HipPart1_L" -p "rig:Hip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007CF";
	addAttr -ci true -k true -sn "twistAmount" -ln "twistAmount" -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "twistAddition" -ln "twistAddition" -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
	setAttr -k on ".twistAmount" 0.33333333333333331;
	setAttr -k on ".twistAddition";
createNode joint -n "rig:HipPart2_L" -p "rig:HipPart1_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007D0";
	addAttr -ci true -k true -sn "twistAmount" -ln "twistAmount" -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "twistAddition" -ln "twistAddition" -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
	setAttr -k on ".twistAmount" 0.66666666666666663;
	setAttr -k on ".twistAddition";
createNode joint -n "rig:Knee_L" -p "rig:HipPart2_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007D1";
	addAttr -ci true -sn "fat" -ln "fat" -dv 5.3747808395268004 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 -7.9057337300926935 ;
	setAttr ".ds" 2;
createNode joint -n "rig:Ankle_L" -p "rig:Knee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007D2";
	addAttr -ci true -sn "fat" -ln "fat" -dv 3.3144481843748594 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".ro" 3;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 5.940888744164643 -3.2284396665911226 7.1034334747240715 ;
	setAttr ".ds" 2;
createNode joint -n "rig:Toes_L" -p "rig:Ankle_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007D3";
	addAttr -ci true -sn "fat" -ln "fat" -dv 2.6873904197633998 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -5.72499700695146 -11.847151218614604 -1.1013412404281553e-13 ;
	setAttr ".r" -type "double3" 8.0229491839916821e-13 1.3596871263258817e-13 3.2599567321245837e-12 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -0.79120452720449364 -3.892253159341974 75.808229210289667 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:ToesEnd_L" -p "rig:Toes_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007D4";
	addAttr -ci true -sn "fat" -ln "fat" -dv 2.6873904197633998 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	setAttr ".t" -type "double3" -6.5710341663822991 -3.8191672047105385e-14 7.9936057773011271e-15 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ssc" no;
	setAttr ".ds" 2;
createNode joint -n "rig:HipFat1_L" -p "rig:Hip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007D5";
	addAttr -ci true -sn "fat" -ln "fat" -dv 8.7444355155545352 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 1.6148669790485997 4.9370587667259107 -0.55956448104938517 ;
	setAttr ".r" -type "double3" 7.1562480332929072e-15 -1.5902773407317587e-14 3.8166656177562201e-14 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 173.73512402025605 10.018203319904833 -47.898367133145499 ;
	setAttr ".ds" 2;
createNode joint -n "rig:HipFatEnd_L" -p "rig:HipFat1_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B424000007D6";
	addAttr -ci true -sn "fat" -ln "fat" -dv 1 -at "double";
	addAttr -ci true -sn "fatY" -ln "fatY" -dv 1 -at "double";
	addAttr -ci true -sn "fatZ" -ln "fatZ" -dv 1 -at "double";
	setAttr ".t" -type "double3" -8.744435515554251 -2.9842794901924208e-13 -8.8817841970012523e-14 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".ds" 2;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "4A0ED900-0000-438E-5D3D-B423000002FC";
	setAttr -s 25 ".lnk";
	setAttr -s 25 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "4A0ED900-0000-438E-5D3D-B423000002FD";
	setAttr ".bsdt[0].bscd" -type "Int32Array" 0 ;
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "4A0ED900-0000-438E-5D3D-B423000002FE";
createNode displayLayerManager -n "layerManager";
	rename -uid "4A0ED900-0000-438E-5D3D-B423000002FF";
	setAttr -s 2 ".dli[1:2]"  4 1;
	setAttr -s 3 ".dli";
createNode displayLayer -n "defaultLayer";
	rename -uid "24566900-0000-06C4-5D33-A82100000248";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "4A0ED900-0000-438E-5D3D-B42300000301";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "24566900-0000-06C4-5D33-A8210000024A";
	setAttr ".g" yes;
createNode animCurveTL -n "persp1_translateX";
	rename -uid "24566900-0000-06C4-5D33-A873000012BF";
	setAttr ".tan" 18;
	setAttr -s 3 ".ktv[0:2]"  1 250.28400149245121 66 93.289357521745586 120 -137.33508952519745;
createNode animCurveTL -n "persp1_translateY";
	rename -uid "24566900-0000-06C4-5D33-A873000012C0";
	setAttr ".tan" 18;
	setAttr -s 3 ".ktv[0:2]"  1 150.86536368944758 66 136.86332099620961 120 151.64186539541095;
createNode animCurveTL -n "persp1_translateZ";
	rename -uid "24566900-0000-06C4-5D33-A873000012C1";
	setAttr ".tan" 18;
	setAttr -s 3 ".ktv[0:2]"  1 218.46157808311023 66 258.53938882404981 120 260.68915268664466;
createNode animCurveTA -n "persp1_rotateX";
	rename -uid "24566900-0000-06C4-5D33-A87C000012C2";
	setAttr ".tan" 18;
	setAttr -s 3 ".ktv[0:2]"  1 -12.338352729602471 66 -11.479830892790609 120 -12.938352729602357;
createNode animCurveTA -n "persp1_rotateY";
	rename -uid "24566900-0000-06C4-5D33-A87C000012C3";
	setAttr ".tan" 18;
	setAttr -s 3 ".ktv[0:2]"  1 48.200000000000216 66 16.60140354708388 120 -26.999999999999861;
createNode animCurveTA -n "persp1_rotateZ";
	rename -uid "24566900-0000-06C4-5D33-A87C000012C4";
	setAttr ".tan" 18;
	setAttr -s 3 ".ktv[0:2]"  1 -2.3858962791964168e-15 66 2.0743132284371617e-16 120 0;
createNode mmMarkerScale -n "mmMarkerScale1";
	rename -uid "24566900-0000-06C4-5D33-A89A000012CD";
createNode animCurveTL -n "marker1_MKR_translateX";
	rename -uid "24566900-0000-06C4-5D33-A8A2000012D0";
	setAttr ".tan" 18;
	setAttr -s 3 ".ktv[0:2]"  1 0.0055527622414874543 66 0.03483656644483888 120 0.14351810189896197;
createNode animCurveTL -n "marker1_MKR_translateY";
	rename -uid "24566900-0000-06C4-5D33-A8A2000012D1";
	setAttr ".tan" 18;
	setAttr -s 3 ".ktv[0:2]"  1 0.14992458051567073 66 0.1247486230073404 120 0.16640909292722647;
createNode script -n "mmSolver_data_node";
	rename -uid "24566900-0000-06C4-5D33-A8CF000012E0";
	addAttr -ci true -sn "mmSolver_data" -ln "mmSolver_data" -dt "string";
	setAttr -l on ".mmSolver_data" -type "string" "{\"display_object_maximum_deviation\": false, \"display_object_frame_deviation\": false, \"display_attribute_state\": true, \"display_object_average_deviation\": false, \"display_object_weight\": true, \"display_attribute_min_max\": false}";
createNode script -n "uiConfigurationScriptNode";
	rename -uid "24566900-0000-06C4-5D33-A8E4000012E1";
	setAttr ".b" -type "string" (
		"// Maya Mel UI Configuration File.\n//\n//  This script is machine generated.  Edit at your own risk.\n//\n//\n\nglobal string $gMainPane;\nif (`paneLayout -exists $gMainPane`) {\n\n\tglobal int $gUseScenePanelConfig;\n\tint    $useSceneConfig = $gUseScenePanelConfig;\n\tint    $menusOkayInPanels = `optionVar -q allowMenusInPanels`;\tint    $nVisPanes = `paneLayout -q -nvp $gMainPane`;\n\tint    $nPanes = 0;\n\tstring $editorName;\n\tstring $panelName;\n\tstring $itemFilterName;\n\tstring $panelConfig;\n\n\t//\n\t//  get current state of the UI\n\t//\n\tsceneUIReplacement -update $gMainPane;\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Top View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Top View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"top\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n"
		+ "            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"base_OpenGL_Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n"
		+ "            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n"
		+ "            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Side View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Side View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"side\" \n"
		+ "            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n"
		+ "            -rendererName \"base_OpenGL_Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n"
		+ "            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Front View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Front View\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"front\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n"
		+ "            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"base_OpenGL_Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n"
		+ "            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Persp View\")) `;\n\tif (\"\" != $panelName) {\n"
		+ "\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"perspShape2\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"wireframe\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n"
		+ "            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"base_OpenGL_Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n"
		+ "            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1981\n            -height 1382\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n"
		+ "\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"ToggledOutliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"ToggledOutliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 0\n            -showReferenceMembers 0\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n"
		+ "            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -isSet 0\n            -isSetMember 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n"
		+ "            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            -renderFilterIndex 0\n            -selectionOrder \"chronological\" \n            -expandAttribute 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"Outliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 0\n            -showReferenceMembers 0\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n"
		+ "            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n"
		+ "            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"graphEditor\" (localizedPanelLabel(\"Graph Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n"
		+ "                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 1\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 1\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n"
		+ "                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 1\n                -displayInfinities 0\n"
		+ "                -displayValues 0\n                -autoFit 1\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -showResults \"off\" \n                -showBufferCurves \"off\" \n                -smoothness \"fine\" \n                -resultSamples 1\n                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -showCurveNames 0\n                -showActiveCurveNames 0\n                -stackedCurves 0\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -displayNormalized 0\n                -preSelectionHighlight 0\n                -constrainDrag 0\n                -classicMode 1\n                -valueLinesToggle 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dopeSheetPanel\" (localizedPanelLabel(\"Dope Sheet\")) `;\n\tif (\"\" != $panelName) {\n"
		+ "\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dope Sheet\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 0\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 0\n                -showCompounds 1\n"
		+ "                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 0\n                -doNotSelectNewObjects 1\n                -dropIsParent 1\n                -transmitFilters 0\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 1\n"
		+ "                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"DopeSheetEd\");\n            dopeSheetEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -outliner \"dopeSheetPanel1OutlineEd\" \n                -showSummary 1\n                -showScene 0\n                -hierarchyBelow 0\n                -showTicks 1\n                -selectionWindow 0 0 0 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"timeEditorPanel\" (localizedPanelLabel(\"Time Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n"
		+ "\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Time Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"clipEditorPanel\" (localizedPanelLabel(\"Trax Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Trax Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = clipEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"sequenceEditorPanel\" (localizedPanelLabel(\"Camera Sequencer\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Camera Sequencer\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = sequenceEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 1 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperGraphPanel\" (localizedPanelLabel(\"Hypergraph Hierarchy\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypergraph Hierarchy\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\n\t\t\t$editorName = ($panelName+\"HyperGraphEd\");\n            hyperGraph -e \n                -graphLayoutStyle \"hierarchicalLayout\" \n                -orientation \"horiz\" \n                -mergeConnections 0\n                -zoom 1\n                -animateTransition 0\n                -showRelationships 1\n                -showShapes 0\n                -showDeformers 0\n                -showExpressions 0\n                -showConstraints 0\n                -showConnectionFromSelected 0\n                -showConnectionToSelected 0\n                -showConstraintLabels 0\n                -showUnderworld 0\n                -showInvisible 0\n                -transitionFrames 1\n                -opaqueContainers 0\n                -freeform 0\n                -imagePosition 0 0 \n                -imageScale 1\n                -imageEnabled 0\n                -graphType \"DAG\" \n                -heatMapDisplay 0\n                -updateSelection 1\n                -updateNodeAdded 1\n                -useDrawOverrideColor 0\n                -limitGraphTraversal -1\n"
		+ "                -range 0 0 \n                -iconSize \"smallIcons\" \n                -showCachedConnections 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"visorPanel\" (localizedPanelLabel(\"Visor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Visor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"createNodePanel\" (localizedPanelLabel(\"Create Node\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Create Node\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"polyTexturePlacementPanel\" (localizedPanelLabel(\"UV Editor\")) `;\n\tif (\"\" != $panelName) {\n"
		+ "\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"UV Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"renderWindowPanel\" (localizedPanelLabel(\"Render View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Render View\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"shapePanel\" (localizedPanelLabel(\"Shape Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tshapePanel -edit -l (localizedPanelLabel(\"Shape Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"posePanel\" (localizedPanelLabel(\"Pose Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n"
		+ "\t\tposePanel -edit -l (localizedPanelLabel(\"Pose Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynRelEdPanel\" (localizedPanelLabel(\"Dynamic Relationships\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dynamic Relationships\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"relationshipPanel\" (localizedPanelLabel(\"Relationship Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Relationship Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"referenceEditorPanel\" (localizedPanelLabel(\"Reference Editor\")) `;\n\tif (\"\" != $panelName) {\n"
		+ "\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Reference Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"componentEditorPanel\" (localizedPanelLabel(\"Component Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Component Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynPaintScriptedPanelType\" (localizedPanelLabel(\"Paint Effects\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Paint Effects\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"scriptEditorPanel\" (localizedPanelLabel(\"Script Editor\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Script Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"profilerPanel\" (localizedPanelLabel(\"Profiler Tool\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Profiler Tool\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"contentBrowserPanel\" (localizedPanelLabel(\"Content Browser\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Content Browser\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"Stereo\" (localizedPanelLabel(\"Stereo\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Stereo\")) -mbv $menusOkayInPanels  $panelName;\nstring $editorName = ($panelName+\"Editor\");\n            stereoCameraView -e \n                -camera \"persp\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"wireframe\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -holdOuts 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 1\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n"
		+ "                -textureDisplay \"modulate\" \n                -textureMaxSize 16384\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -depthOfFieldPreview 1\n                -maxConstantTransparency 1\n                -objectFilterShowInHUD 1\n                -isFiltered 0\n                -colorResolution 4 4 \n                -bumpResolution 4 4 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 0\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n"
		+ "                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -imagePlane 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -clipGhosts 1\n"
		+ "                -greasePencils 1\n                -shadows 0\n                -captureSequenceNumber -1\n                -width 0\n                -height 0\n                -sceneRenderFilter 0\n                -displayMode \"centerEye\" \n                -viewColor 0 0 0 1 \n                -useCustomBackground 1\n                $editorName;\n            stereoCameraView -e -viewSelected 0 $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperShadePanel\" (localizedPanelLabel(\"Hypershade\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypershade\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"nodeEditorPanel\" (localizedPanelLabel(\"Node Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -defaultPinnedState 0\n                -additiveGraphingMode 0\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                -activeTab -1\n                -editorMode \"default\" \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n"
		+ "\t\t}\n\t}\n\n\n\tif ($useSceneConfig) {\n        string $configName = `getPanel -cwl (localizedPanelLabel(\"Current Layout\"))`;\n        if (\"\" != $configName) {\n\t\t\tpanelConfiguration -edit -label (localizedPanelLabel(\"Current Layout\")) \n\t\t\t\t-userCreated false\n\t\t\t\t-defaultImage \"vacantCell.xP:/\"\n\t\t\t\t-image \"\"\n\t\t\t\t-sc false\n\t\t\t\t-configString \"global string $gMainPane; paneLayout -e -cn \\\"single\\\" -ps 1 100 100 $gMainPane;\"\n\t\t\t\t-removeAllPanels\n\t\t\t\t-ap false\n\t\t\t\t\t(localizedPanelLabel(\"Persp View\")) \n\t\t\t\t\t\"modelPanel\"\n"
		+ "\t\t\t\t\t\"$panelName = `modelPanel -unParent -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels `;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -camera \\\"perspShape2\\\" \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"wireframe\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 16384\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"base_OpenGL_Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1981\\n    -height 1382\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName\"\n"
		+ "\t\t\t\t\t\"modelPanel -edit -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels  $panelName;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -camera \\\"perspShape2\\\" \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"wireframe\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 16384\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"base_OpenGL_Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1981\\n    -height 1382\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName\"\n"
		+ "\t\t\t\t$configName;\n\n            setNamedPanelLayout (localizedPanelLabel(\"Current Layout\"));\n        }\n\n        panelHistory -e -clear mainPanelHistory;\n        sceneUIReplacement -clear;\n\t}\n\n\ngrid -spacing 5 -size 12 -divisions 5 -displayAxes yes -displayGridLines yes -displayDivisionLines yes -displayPerspectiveLabels no -displayOrthographicLabels no -displayAxesBold yes -perspectiveLabelPosition axis -orthographicLabelPosition edge;\nviewManip -drawCompass 0 -compassAngle 0 -frontParameters \"\" -homeParameters \"\" -selectionLockParameters \"\";\n}\n");
	setAttr ".st" 3;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "24566900-0000-06C4-5D33-A8E4000012E2";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 120 -ast 1 -aet 200 ";
	setAttr ".st" 6;
createNode renderLayerManager -n "rig:renderLayerManager";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000D18";
createNode renderLayer -n "rig:defaultRenderLayer";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000D19";
	setAttr ".g" yes;
createNode reference -n "rig:woman_modelRN";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000D1A";
	setAttr ".phl[1]" 0;
	setAttr ".ed" -type "dataReferenceEdits" 
		"rig:woman_modelRN"
		"woman_modelRN" 4
		2 "|woman_model:geo|woman_model:bikini|woman_model:bikiniShape" "intermediateObject" 
		" 1"
		2 "|woman_model:geo|woman_model:bikini|woman_model:bikiniShape" "dispResolution" 
		" 1"
		2 "|woman_model:geo|woman_model:bikini|woman_model:bikiniShape" "displaySmoothMesh" 
		" 0"
		5 3 "rig:woman_modelRN" "|woman_model:geo|woman_model:bikini|woman_model:bikiniShape.worldMesh" 
		"rig:woman_modelRN.placeHolderList[1]" "";
	setAttr ".ptag" -type "string" "";
lockNode -l 1 ;
createNode ikRPsolver -n "rig:ikRPsolver";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000D40";
createNode dagPose -n "rig:bindPose23";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000D42";
	setAttr -s 88 ".wm";
	setAttr ".wm[0]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[1]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[2]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[81]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[82]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[83]" -type "matrix" 1 0 0 0 0 0.99999999999999978 0 0
		 0 0 1 0 -1.8275984745877472e-13 143.65649237269599 0.32023587761595307 1;
	setAttr ".wm[98]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 -1.4447870254516602 151.19853210449222 10.28009510040283 1;
	setAttr ".wm[100]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 -4.2734475135803223 151.69573974609375 9.1910829544067365 1;
	setAttr ".wm[102]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 -5.6632189750671378 150.33395385742188 6.9529762268066406 1;
	setAttr ".wm[104]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 1.4447870254516602 151.19853210449222 10.28009510040283 1;
	setAttr ".wm[106]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 4.2734475135803223 151.69573974609375 9.1910829544067365 1;
	setAttr ".wm[108]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 5.6632189750671378 150.33395385742188 6.9529762268066406 1;
	setAttr -s 112 ".xm";
	setAttr ".xm[0]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[1]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[2]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[3]" -type "matrix" "xform" 1 1 1 0 0 0 0 -5.8064397712757788e-15
		 88.867637422588331 0.47329046439253208 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.50758331815289393 0.49229988333626273 0.50758331815289404 0.49229988333626312 1
		 1 1 yes;
	setAttr ".xm[4]" -type "matrix" "xform" 1 1 1 0 -1.3877787807814457e-17 0 2 -7.3216659883418345
		 -2.1522866108679581 -8.8414397624647592 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.023498253370695169 -0.99834971054101485 0.043966139000687576 0.028507300338171695 1
		 1 1 yes;
	setAttr ".xm[5]" -type "matrix" "xform" 1 1 1 0 0 0 2 12.439033508293349
		 -1.3579148809228503e-05 2.1671553440683056e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[6]" -type "matrix" "xform" 1 1 1 0 0 0 2 12.439033508293385
		 -1.3579148809152175e-05 2.2115642650533118e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[7]" -type "matrix" "xform" 1 1 1 0 0 1.0897223354234247e-06 2 12.439033508293356
		 -1.3579148809894637e-05 2.2026824808563106e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.068935825723656377 0.99762109637466956 1
		 1 1 yes;
	setAttr ".xm[8]" -type "matrix" "xform" 1 1 1 -5.3461489324973089e-08 -1.2041855584009298e-07 -8.8494812641806198e-07 3 37.335575103759759
		 -1.2168044349891716e-13 1.1312075898217699e-07 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.053443509429542964 -0.02486884457531369 0.063298645820076826 0.9962522839656065 1
		 1 1 yes;
	setAttr ".xm[9]" -type "matrix" "xform" 1 1 1 1.5494550087424806e-14 1.0477729794904721e-15 6.2061358656328977e-14 5 5.7249970069515586
		 11.847151218614579 1.1546319456101628e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.015417631002365101 -0.03103427067509509 0.61378786716892175 0.78871010188418766 1
		 1 1 no;
	setAttr ".xm[10]" -type "matrix" "xform" 1 1 1 -2.4074124304840448e-35 -6.9388939039072284e-18 -6.9388939039072284e-18 2 -7.3216659883417634
		 -2.1522866108679586 8.8414397624647325 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.99834971054101485 0.023498253370694656 -0.028507300338170172 0.043966139000687632 1
		 1 1 yes;
	setAttr ".xm[11]" -type "matrix" "xform" 1 1 1 1.9428902930940212e-16 3.6082248300317602e-16 -1.5543122344752192e-15 0 1.6148669790486281
		 4.9370587667259089 -0.55956448104940915 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.91099198292552752 -0.39941134458514299 -0.10177431157513424 0.014358773119978137 1
		 1 1 yes;
	setAttr ".xm[12]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.3816508661516735
		 -3.1086244689504383e-15 -3.7860044429179921e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[13]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.3816508661518867
		 1.7763568394002505e-15 -7.5403910957633823e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[14]" -type "matrix" "xform" 1 1 1 0 0 3.0531133177191805e-16 0 3.3816508661515314
		 -3.5527136788005009e-15 -1.8866786634444164e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.059683120475990704 0.99821737368683805 1
		 1 1 yes;
	setAttr ".xm[15]" -type "matrix" "xform" 1 1 1 0 0 2.9143354396410359e-16 0 11.252214457917404
		 1.7763568394002505e-15 -3.5754913018389324e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.043988873638582705 0.99903202100633837 1
		 1 1 yes;
	setAttr ".xm[16]" -type "matrix" "xform" 1 1 1 -4.1633363423443789e-17 -3.6082248300317583e-16 2.3314683517128287e-15 0 -1.6148669790486849
		 -4.9370587667259116 0.55956448104938605 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.91099198292552752 -0.39941134458514305 -0.10177431157513461 0.014358773119978206 1
		 1 1 yes;
	setAttr ".xm[17]" -type "matrix" "xform" 1 1 1 0 0 3.0531133177191805e-16 0 12.624062549953095
		 1.4210854715202004e-14 -3.6544896322720374e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.063202616704989389 0.99800071605267004 1
		 1 1 yes;
	setAttr ".xm[18]" -type "matrix" "xform" 1 1 1 -8.326672684688676e-16 3.4694469519535982e-17 3.8857805861880484e-16 2 4.8146220815627316
		 3.4256949883352346 -1.1096741025741683 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.18589095985181586 0.67951199491462866 -0.10062215226822624 0.70255475394123001 1
		 1 1 yes;
	setAttr ".xm[19]" -type "matrix" "xform" 1 1 1 2.8310687127941492e-15 -5.9674487573602233e-16 -4.7184478546569064e-16 5 14.409854929115925
		 -3.0198066269804258e-14 3.836930773104541e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.18172647704095962 0.62214217906889968 0.2135164950494772 0.73097558297625054 1
		 1 1 yes;
	setAttr ".xm[20]" -type "matrix" "xform" 1 1 1 0 0 0 5 9.5365921587067959
		 -7.1054273576010019e-15 -4.2632564145606011e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[21]" -type "matrix" "xform" 1 1 1 0 0 0 5 9.5365921587067675
		 -3.5527136788005009e-15 -2.1316282072803006e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[22]" -type "matrix" "xform" 1 1 1 0 0 -6.106226635438361e-16 5 9.5365921587067959
		 0 -2.8421709430404007e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.21119289257827159 0.97744440359767915 1
		 1 1 yes;
	setAttr ".xm[23]" -type "matrix" "xform" 1 1 1 0 0 0 5 7.5870240637033817
		 1.4210854715202004e-14 9.9475983006414026e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[24]" -type "matrix" "xform" 1 1 1 0 0 0 5 7.5870240637034527
		 1.7763568394002505e-14 8.5265128291212022e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[25]" -type "matrix" "xform" 1 1 1 -1.3168719587008941e-15 -7.2511441295830458e-16 -1.1313988483065144e-15 5 7.5870240637034669
		 7.1054273576010019e-15 9.2370555648813024e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.041669116909086645 -0.00058589047046050946 0.10049952459482558 0.99406397529766033 1
		 1 1 yes;
	setAttr ".xm[26]" -type "matrix" "xform" 1 1 1 1.1102230246251565e-16 1.2750217548429532e-16 9.0205620750793957e-17 5 8.7083736116588142
		 -1.9121430819271978 0.57542589341604611 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.021057171555371519 0.22495986668851095 -0.12548867043840622 0.96602393733135616 1
		 1 1 no;
	setAttr ".xm[27]" -type "matrix" "xform" 1 1 1 -4.3368086899420177e-16 5.2095914387928402e-17 3.8966226079129029e-16 5 2.9299735768954491
		 2.8421709430404007e-14 -2.5313084961453569e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0041471581112502423 0.22568814001149612 -0.016301903414309926 0.97405436834030079 1
		 1 1 no;
	setAttr ".xm[28]" -type "matrix" "xform" 1 1 1 -7.5286998857393467e-16 5.2388648974499535e-16 1.1310397063368784e-15 5 9.0507967385055608
		 2.1316282072803006e-14 -2.1316282072803006e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.13576760484131239 0.16285044170192289 -0.095943933091941241 0.97254390791161249 1
		 1 1 no;
	setAttr ".xm[29]" -type "matrix" "xform" 1 1 1 -4.9983075404297342e-16 -1.1093249546341108e-16 1.336665424612332e-15 5 2.6150711681148238
		 3.1974423109204508e-14 -2.4868995751603507e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 4.2036359576253032e-05 0.23352034459464968 0.00017407681138761921 0.97235189956651202 1
		 1 1 no;
	setAttr ".xm[30]" -type "matrix" "xform" 1 1 1 -3.4136105400706107e-16 -5.1201447595628052e-17 6.2645201526212446e-16 5 2.2798674841393023
		 -1.0658141036401503e-14 -7.1054273576010019e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.014226627620729361 0.050664508358946952 -0.0013156844410576883 0.99861352866548858 1
		 1 1 no;
	setAttr ".xm[31]" -type "matrix" "xform" 1 1 1 0 0 6.106226635438361e-16 5 10.316790868949951
		 2.3980817331903381e-14 1.8836197044295709e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.17276085650730627 0.98496379956771096 1
		 1 1 yes;
	setAttr ".xm[32]" -type "matrix" "xform" 1 1 1 0 0 0 5 1.2444419780076714
		 5.6843418860808015e-14 -6.7037896900691453e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[33]" -type "matrix" "xform" 1 1 1 0 0 0 5 1.2444419780077141
		 -1.4210854715202004e-14 -9.0525235226197976e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[34]" -type "matrix" "xform" 1 1 1 0 0 0 0 1.2444419780078988
		 -3.5527136788005009e-14 -1.5703918726894392e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[35]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.7333259340232985
		 7.1054273576010019e-14 -4.0451615808562826e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[36]" -type "matrix" "xform" 1 1 1 0 0 -1.4432899320127035e-15 5 3.7333259340227016
		 -3.5527136788005009e-14 -4.0536062172672702e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.14789458303942959 0.98900313058533507 1
		 1 1 yes;
	setAttr ".xm[37]" -type "matrix" "xform" 1 1 1 2.2204460492503131e-15 4.4408920985006281e-16 2.220446049250318e-16 2 4.8146220815627174
		 3.4256949883352239 1.1096741025742154 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.6795119949146271 -0.18589095985181581 0.70255475394123157 0.10062215226822596 1
		 1 1 yes;
	setAttr ".xm[38]" -type "matrix" "xform" 1 1 1 -8.6042284408449632e-15 -2.6367796834848079e-16 1.4155343563970734e-15 5 -14.409854929115903
		 -3.907985046680551e-14 -4.5474735088646412e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.18172647704095798 0.6221421790688999 0.2135164950494754 0.73097558297625131 1
		 1 1 yes;
	setAttr ".xm[39]" -type "matrix" "xform" 1 1 1 0 0 0 5 -9.5365921587066964
		 3.5527136788005009e-15 -2.1316282072803006e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[40]" -type "matrix" "xform" 1 1 1 0 0 0 5 -9.5365921587067248
		 -3.5527136788005009e-15 -1.4210854715202004e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[41]" -type "matrix" "xform" 1 1 1 0 0 1.3322676295501878e-15 5 -9.5365921587067533
		 -3.5527136788005009e-15 -1.4210854715202004e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.21119289257827203 0.97744440359767903 1
		 1 1 yes;
	setAttr ".xm[42]" -type "matrix" "xform" 1 1 1 0 0 0 5 -7.5870240637034527
		 -1.4210854715202004e-14 -7.815970093361102e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[43]" -type "matrix" "xform" 1 1 1 0 0 0 5 -7.5870240637034811
		 -1.0658141036401503e-14 -8.5265128291212022e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[44]" -type "matrix" "xform" 1 1 1 1.4528309111305571e-17 3.2439329000766293e-16 1.1542551853552241e-15 5 -7.5870240637034669
		 -3.5527136788005009e-15 -7.1054273576010019e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.041669116909086514 -0.00058589047046022757 0.1004995245948251 0.99406397529766044 1
		 1 1 yes;
	setAttr ".xm[45]" -type "matrix" "xform" 1 1 1 2.9837243786801092e-16 2.4286128663675289e-16 -8.2572837456496028e-16 5 -9.0507967385055679
		 1.4210854715202004e-14 6.3948846218409017e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.13576760484131209 0.16285044170192203 -0.095943933091939326 0.97254390791161294 1
		 1 1 no;
	setAttr ".xm[46]" -type "matrix" "xform" 1 1 1 -1.422473250300984e-16 -6.6613381477509353e-16 -7.9103390504542374e-16 5 3.0055150379940585
		 0.51952218981558218 -1.7089693953339022 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.70491332856195099 0.057259404968380584 0.14078947718753435 0.69281807343027535 1
		 1 1 no;
	setAttr ".xm[47]" -type "matrix" "xform" 1 1 1 -2.7755575615628899e-16 -8.9012998361059914e-16 3.5561831257524536e-16 5 4.0601659831538441
		 1.2434497875801753e-14 1.0658141036401503e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.017239913876694303 0.13220968231244329 -0.032448616463766275 0.99054049516511666 1
		 1 1 no;
	setAttr ".xm[48]" -type "matrix" "xform" 1 1 1 0 0 0 5 2.150473604285196
		 -2.6645352591003757e-14 -3.907985046680551e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 no;
	setAttr ".xm[49]" -type "matrix" "xform" 1 1 1 -3.5000756633263312e-16 9.9926349855368876e-16 2.9433378477550251e-16 5 -2.615071168114838
		 0 4.9737991503207013e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 4.2036359576364027e-05 0.23352034459464976 0.00017407681138764683 0.97235189956651202 1
		 1 1 no;
	setAttr ".xm[50]" -type "matrix" "xform" 1 1 1 -3.2092384305571073e-17 1.0092905786303341e-15 2.7798943702528334e-16 5 -2.279867484139416
		 4.2632564145606011e-14 4.7961634663806763e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.014226627620729263 0.05066450835894689 -0.0013156844410580077 0.99861352866548858 1
		 1 1 no;
	setAttr ".xm[51]" -type "matrix" "xform" 1 1 1 -2.3592239273284581e-16 8.7343327015432237e-16 1.0581813203458533e-16 5 -8.7083736116588923
		 1.9121430819271978 -0.57542589341603545 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.021057171555371495 0.2249598666885107 -0.12548867043840439 0.96602393733135661 1
		 1 1 no;
	setAttr ".xm[52]" -type "matrix" "xform" 1 1 1 1.1275702593849294e-17 1.2211369068704236e-15 -7.8279396853453432e-17 5 -2.9299735768954633
		 4.9737991503207013e-14 2.708944180085382e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0041471581112503273 0.22568814001149617 -0.016301903414310093 0.97405436834030079 1
		 1 1 no;
	setAttr ".xm[53]" -type "matrix" "xform" 1 1 1 -1.8686224442787671e-16 8.8821560974046581e-16 2.733544727379087e-17 5 -2.3283439685008034
		 -3.1974423109204508e-14 7.815970093361102e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.00046031140391352587 0.13137067866208843 7.2721475625731112e-05 0.99133320715734163 1
		 1 1 no;
	setAttr ".xm[54]" -type "matrix" "xform" 1 1 1 1.5439038936193586e-16 2.4990860075790877e-16 1.618442792977737e-16 0 -2.5323556682532242
		 1.7906199654992889 -0.35330912270260839 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0020024495612333579 -0.024806957744675912 -0.08043465652188804 0.99644913120209722 1
		 1 1 no;
	setAttr ".xm[55]" -type "matrix" "xform" 1 1 1 -9.7144514654701456e-17 8.7430063189231058e-16 6.5225602696727927e-16 5 -4.5250926779440306
		 2.3533218848592483 0.44446663353520677 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.21720450480376374 0.16480569297956635 -0.17161255283830726 0.94668390625530119 1
		 1 1 no;
	setAttr ".xm[56]" -type "matrix" "xform" 1 1 1 1.1602318498310509e-16 1.1099143869950006e-15 -1.2771901591879247e-16 5 -2.1075383328532382
		 7.815970093361102e-14 -1.5543122344752192e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0022402842450934572 0.20223921632159 -0.00020873341998559129 0.9793335677584476 1
		 1 1 no;
	setAttr ".xm[57]" -type "matrix" "xform" 1 1 1 -4.8789097761847786e-17 1.3904486286311914e-15 1.066854937725737e-16 5 -1.5833293982736762
		 -5.8619775700208265e-14 3.5527136788005009e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.018463746298894666 0.18215708418089929 0.0031855123646682155 0.98309091098753298 1
		 1 1 no;
	setAttr ".xm[58]" -type "matrix" "xform" 1 1 1 -6.7307270867900194e-16 6.4878658001532506e-16 2.4008572907519014e-15 5 -5.5468274631968058
		 0.87121337525206854 -0.085476270302706325 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.060144891309412349 0.23155651288564583 -0.09274792423305124 0.96652056157128841 1
		 1 1 no;
	setAttr ".xm[59]" -type "matrix" "xform" 1 1 1 -8.8893736122086528e-16 9.9634791519628781e-16 7.9320230939039524e-16 5 -2.5823924595557628
		 6.7501559897209518e-14 4.8960835385969403e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.0024919881517539836 0.21918116287178402 -0.00064221548926046723 0.9756807856038211 1
		 1 1 no;
	setAttr ".xm[60]" -type "matrix" "xform" 1 1 1 -5.6131856975005847e-16 1.3361631340746104e-15 6.9063678387326682e-16 5 -2.2923824975695055
		 1.7763568394002505e-14 4.9737991503207013e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0049183923914902531 0.084049853359414534 0.00049023492454319806 0.99644929185396247 1
		 1 1 no;
	setAttr ".xm[61]" -type "matrix" "xform" 1 1 1 -6.5225602696727947e-16 -8.3266726846886938e-17 5.9674487573602164e-16 5 -3.0055150379941793
		 -0.51952218981555376 1.7089693953339378 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.70491332856195121 0.057259404968379099 0.14078947718753526 0.69281807343027546 1
		 1 1 no;
	setAttr ".xm[62]" -type "matrix" "xform" 1 1 1 -6.9388939039072296e-17 5.9847959921199832e-17 3.0010716134398763e-16 5 -4.0601659831538015
		 -2.8421709430404007e-14 -7.1054273576010019e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.017239913876694518 0.13220968231244346 -0.032448616463766219 0.99054049516511666 1
		 1 1 no;
	setAttr ".xm[63]" -type "matrix" "xform" 1 1 1 0 0 0 5 -2.1504736042852102
		 3.0198066269804258e-14 5.6843418860808015e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 no;
	setAttr ".xm[64]" -type "matrix" "xform" 1 1 1 4.9960036108132044e-16 4.9960036108132025e-16 3.3306690738754706e-16 0 7.184014322817319
		 7.9495028875399925 -6.6289249529645113 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.327180291614668 -0.91247968200079466 0.2152222281462921 -0.11837769733532902 1
		 1 1 yes;
	setAttr ".xm[65]" -type "matrix" "xform" 1 1 1 -3.1918911957973251e-16 1.110223024625157e-16 3.3306690738754696e-16 0 7.1840143228174043
		 7.9495028875400031 6.6289249529645256 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.91247968200079443 0.32718029161466866 0.11837769733533096 0.21522222814629144 1
		 1 1 yes;
	setAttr ".xm[66]" -type "matrix" "xform" 1 1 1 0 0 0 2 -12.439033508293377
		 1.357914879600991e-05 8.9706020389712648e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[67]" -type "matrix" "xform" 1 1 1 0 0 0 2 -12.43903350829337
		 1.357914879494132e-05 8.5265128291212022e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[68]" -type "matrix" "xform" 1 1 1 0 0 1.0900276630477197e-06 2 -12.439033508293356
		 1.357914879557276e-05 8.6153306710912148e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.068935825723658556 0.99762109637466934 1
		 1 1 yes;
	setAttr ".xm[69]" -type "matrix" "xform" 1 1 1 -5.0189667018617259e-08 -1.1406555332132297e-07 -8.8582498902396052e-07 3 -37.335575103759787
		 0 8.8817841970012523e-16 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.053443509429542548 -0.024868844575313187 0.063298645820076979 0.99625228396560661 1
		 1 1 yes;
	setAttr ".xm[70]" -type "matrix" "xform" 1 1 1 1.2843892616132237e-14 1.4779844015325773e-15 5.2595189488358038e-14 5 -5.7249970069515159
		 -11.847151218614588 -1.2434497875801753e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.01541763100236512 -0.031034270675095191 0.61378786716892264 0.788710101884187 1
		 1 1 no;
	setAttr ".xm[71]" -type "matrix" "xform" 1 1 1 -4.8138576458356377e-16 4.4300500767757736e-16 1.009893666088779e-15 0 2.5323556682531319
		 -1.790619965499296 0.35330912270261194 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0020024495612329394 -0.024806957744675433 -0.080434656521889844 0.9964491312020971 1
		 1 1 no;
	setAttr ".xm[72]" -type "matrix" "xform" 1 1 1 3.8857805861880474e-16 1.3704315460216759e-16 -7.3552275381416611e-16 5 5.5468274631967915
		 -0.87121337525204012 0.085476270302706325 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.060144891309412515 0.23155651288564597 -0.092747924233051629 0.96652056157128841 1
		 1 1 no;
	setAttr ".xm[73]" -type "matrix" "xform" 1 1 1 -4.2572892368537845e-16 5.5639331138979007e-17 1.6055678921794714e-16 5 2.3283439685009526
		 1.4210854715202004e-14 -5.3290705182007514e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.00046031140391369901 0.13137067866208857 7.2721475625592334e-05 0.99133320715734152 1
		 1 1 no;
	setAttr ".xm[74]" -type "matrix" "xform" 1 1 1 1.0824674490095278e-15 2.91433543964103e-16 -1.0824674490095278e-15 5 4.5250926779440093
		 -2.3533218848591986 -0.44446663353525651 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.21720450480376369 0.16480569297956579 -0.17161255283830715 0.9466839062553013 1
		 1 1 no;
	setAttr ".xm[75]" -type "matrix" "xform" 1 1 1 1.2347300916079607e-15 5.2801386953872248e-17 -1.074661193367632e-15 5 2.107538332853494
		 -2.8421709430404007e-14 -5.7065463465733046e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0022402842450937074 0.20223921632159039 -0.00020873341998595157 0.97933356775844749 1
		 1 1 no;
	setAttr ".xm[76]" -type "matrix" "xform" 1 1 1 3.0574501264091225e-15 2.8189256484622462e-17 -4.2674197509029459e-16 5 1.5833293982734915
		 4.7961634663806763e-14 3.5527136788005009e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.018463746298894881 0.18215708418089915 0.0031855123646680793 0.98309091098753298 1
		 1 1 no;
	setAttr ".xm[77]" -type "matrix" "xform" 1 1 1 4.3107878378023656e-16 6.11867378459826e-16 -3.2135752392470356e-16 5 2.5823924595557912
		 1.4210854715202004e-14 -8.0158102377936302e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.0024919881517543332 0.21918116287178399 -0.00064221548925996773 0.9756807856038211 1
		 1 1 no;
	setAttr ".xm[78]" -type "matrix" "xform" 1 1 1 1.0751084267637827e-15 8.5712365075494072e-16 -4.8355416892853557e-16 5 2.2923824975696974
		 -2.4868995751603507e-14 2.1316282072803006e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0049183923914904006 0.084049853359414659 0.00049023492454322603 0.99644929185396247 1
		 1 1 no;
	setAttr ".xm[79]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.3816508661516451
		 -3.9968028886505635e-15 -3.7860044429179921e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[80]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.3816508661518583
		 2.6645352591003757e-15 -7.5403910957633697e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[81]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[82]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[83]" -type "matrix" "xform" 0.99999999999999989 0.99999999999999978 1 3.8857805861880464e-16 -2.2204460492503131e-16 2.7755575615628904e-16 0 -1.8275984745877472e-13
		 143.65649237269599 0.32023587761595307 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[84]" -type "matrix" "xform" 1 1 1 0 0 0 2 -3.1112243901128878
		 5.8929440352700055 6.6794374243201426 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.70710678118654913 -4.3297802811774566e-17 -0.70710678118654591 4.3297802811774763e-17 1
		 1 1 no;
	setAttr ".xm[85]" -type "matrix" "xform" 1 1 1 0 0 0 2 3.1112243901132541
		 5.8929440352699771 6.6794374243201231 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.70710678118654913 -4.3297802811774566e-17 -0.70710678118654591 4.3297802811774763e-17 1
		 1 1 no;
	setAttr ".xm[86]" -type "matrix" "xform" 1.0000000000000002 1.0000000000000004 1.0000000000000002 0 0 0 0 0.003302216530028951
		 0.71905694371025675 4.3749627309463968 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 no;
	setAttr ".xm[87]" -type "matrix" "xform" 1.0000000000000002 1.0000000000000004 1.0000000000000002 0 0 0 0 -0.0028511285780032747
		 -1.6616803609772433 4.2229955873064746 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 no;
	setAttr ".xm[88]" -type "matrix" "xform" 1 1 1 0 0 0 0 -1.8233666953346861e-13
		 143.65649237269602 0.32023587761597172 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[89]" -type "matrix" "xform" 0.99999999999999978 0.99999999999999978 0.99999999999999978 0 0 0 0 1.8233666953346863e-13
		 0.99156365757741582 2.1710201209954785 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 no;
	setAttr ".xm[90]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 -5.66009521484375 6.1866567134857187 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1.0000000000000002
		 1.0000000000000002 1.0000000000000002 yes;
	setAttr ".xm[91]" -type "matrix" "xform" 1 1 1 0 0 0 0 -0.0015106201171875
		 -0.80441868305206299 8.9281749725341797 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[92]" -type "matrix" "xform" 1 1.0000000000000002 1 0 0 0 0 -3.1112243901128878
		 5.8929440352700055 6.6794374243201418 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 no;
	setAttr ".xm[93]" -type "matrix" "xform" 1 1.0000000000000002 1 0 0 0 0 3.1112243901132528
		 5.8929440352700055 6.6794374243201418 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 no;
	setAttr ".xm[94]" -type "matrix" "xform" 1 1 1 0 0 0 0 1.8275984745877472e-13
		 -0.94380513475510952 4.6291029357450206 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.16651786912226402 -0.68722034258524411 0.16651786912226402 0.68722034258524434 1
		 1 1 no;
	setAttr ".xm[95]" -type "matrix" "xform" 1 1 1 0 0 0 0 1.3052331395743977
		 4.2632564145606011e-14 4.3472996521776729e-16 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.20299453799068815 0.97917986986352368 1
		 1 1 yes;
	setAttr ".xm[96]" -type "matrix" "xform" 1 1 1 0 0 0 0 0.81165748224761636
		 8.5265128291212022e-14 2.749239935531449e-16 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.083081342678300696 0.99654276902638295 1
		 1 1 yes;
	setAttr ".xm[97]" -type "matrix" "xform" 1 1 1 0 0 0 0 0.87678936592238976
		 -2.2737367544323206e-13 2.8475485182908648e-16 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.076229233628500176 0.99709031884800259 1
		 1 1 yes;
	setAttr ".xm[98]" -type "matrix" "xform" 1 1.0000000000000002 1 0 0 0 0 -1.4447870254514774
		 7.5420397317962227 9.9598592227868767 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[99]" -type "matrix" "xform" 1 1 1 0 0 0 0 2.2204460492503131e-16
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[100]" -type "matrix" "xform" 1 1.0000000000000002 1 0 0 0 0 -4.2734475135801393
		 8.0392473733977567 8.870847076790783 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[101]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 -2.8421709430404007e-14 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[102]" -type "matrix" "xform" 1 1.0000000000000002 1 0 0 0 0 -5.6632189750669548
		 6.6774614847258817 6.6327403491906871 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[103]" -type "matrix" "xform" 1 1 1 0 0 0 0 -8.8817841970012523e-16
		 0 8.8817841970012523e-16 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[104]" -type "matrix" "xform" 1 1.0000000000000002 1 0 0 0 0 1.4447870254518429
		 7.5420397317962227 9.9598592227868767 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[105]" -type "matrix" "xform" 1 1 1 0 0 0 0 -2.2204460492503131e-16
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[106]" -type "matrix" "xform" 1 1.0000000000000002 1 0 0 0 0 4.2734475135805052
		 8.0392473733977567 8.870847076790783 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[107]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 -2.8421709430404007e-14 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[108]" -type "matrix" "xform" 1 1.0000000000000002 1 0 0 0 0 5.6632189750673207
		 6.6774614847258817 6.6327403491906871 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[109]" -type "matrix" "xform" 1 1 1 0 0 0 0 8.8817841970012523e-16
		 0 8.8817841970012523e-16 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[110]" -type "matrix" "xform" 1 1 1 0 0 0 0 1.827598474587747e-13
		 5.4188641718357928 2.1710201209954971 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[111]" -type "matrix" "xform" 1 1 1 0 0 0 0 1.8275984745877472e-13
		 4.9761282827722368 2.1710201209954971 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr -s 83 ".m";
	setAttr -s 97 ".p";
	setAttr -s 112 ".g[0:111]" yes yes yes no no no no no no no no no no 
		no no no no no no no no no no no no no no no no no no no no no no no no no no no 
		no no no no no no no no no no no no no no yes no no no no no no no no no no no no 
		no no no no yes no no no no no no no yes yes yes yes yes no no no no yes no no no 
		no no yes yes yes no yes no yes no yes no yes no yes no yes no no no;
	setAttr ".bp" yes;
createNode dagPose -n "rig:bindPose15";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000D43";
	setAttr -s 79 ".wm";
	setAttr ".wm[0]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[1]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[2]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[3]" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -5.8064397712757504e-15 88.867637422588331 0.47329046439253697 1;
	setAttr ".wm[4]" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -8.4661282183400888e-15 92.247708493863087 0.57664487251233765 1;
	setAttr ".wm[5]" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -1.4880203318250076e-14 95.62777956513807 0.67999928063214798 1;
	setAttr ".wm[6]" -type "matrix" 3.9022319828289044e-16 0.99605373441152567 -0.088752229069772509 0 -4.5635506035450343e-16 0.088752229069772565 0.99605373441152578 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -3.2620673956841366e-14 99.007850636412726 0.78335368875194566 1;
	setAttr ".wm[7]" -type "matrix" 4.2882324480567274e-16 0.98439830163183939 -0.17595449339062028 0 -4.2029122082625582e-16 0.1759544933906203 0.9843983016318395 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -6.3538155657931891e-14 110.21566086762064 -0.2153054263593237 1;
	setAttr ".wm[8]" -type "matrix" 3.7237652132655529e-16 0.99873090588638569 -0.050364448049781949 0 -4.7103058494541948e-16 0.05036444804978199 0.9987309058863858 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -9.3803574503953694e-14 122.64276660148867 -2.4365659568678506 1;
	setAttr ".wm[9]" -type "matrix" -0.86555019344236128 -0.16717919135475579 -0.47209530882001027 0 -0.4147111464715928 -0.28922999948722544 0.86276339305097827 0
		 -0.28078021230868089 0.94254820851486931 0.18101200789257746 0 -1.1096741025743033 130.16265236880656 2.4663549575535777 1;
	setAttr ".wm[10]" -type "matrix" -0.17960524299256644 -0.98248094674772968 -0.049730734634288815 0 0.28084335038909258 -0.099658096810002053 0.95456549082943365 0
		 -0.94279847752942958 0.15747842080073426 0.29382235747181712 0 -14.741907198981476 127.52961534486117 -4.9690466428543587 1;
	setAttr ".wm[11]" -type "matrix" -0.17960524299256644 -0.98248094674772968 -0.049730734634288815 0 0.28084335038909258 -0.099658096810002053 0.95456549082943365 0
		 -0.94279847752942958 0.15747842080073426 0.29382235747181712 0 -16.396031177095228 118.48118632921928 -5.4270555474785969 1;
	setAttr ".wm[12]" -type "matrix" -0.17960524299256644 -0.98248094674772968 -0.049730734634288815 0 0.28084335038909258 -0.099658096810002053 0.95456549082943365 0
		 -0.94279847752942958 0.15747842080073426 0.29382235747181712 0 -18.050155155208973 109.43275731357741 -5.8850644521028368 1;
	setAttr ".wm[13]" -type "matrix" -0.04627468285217369 -0.93467789007364943 0.35247112723512786 0 0.3301358576330663 0.3187127057234741 0.88850015572047136 0
		 -0.94279847752942958 0.15747842080073426 0.29382235747181712 0 -19.704279133322725 100.38432829793551 -6.3430733567270696 1;
	setAttr ".wm[14]" -type "matrix" -0.04627468285217369 -0.93467789007364943 0.35247112723512786 0 0.3301358576330663 0.3187127057234741 0.88850015572047136 0
		 -0.94279847752942958 0.15747842080073426 0.29382235747181712 0 -20.062330188524818 93.152244052559936 -3.6158227035356463 1;
	setAttr ".wm[15]" -type "matrix" -0.04627468285217369 -0.93467789007364943 0.35247112723512786 0 0.3301358576330663 0.3187127057234741 0.88850015572047136 0
		 -0.94279847752942958 0.15747842080073426 0.29382235747181712 0 -20.420381243726901 85.920159807184348 -0.88857205034421671 1;
	setAttr ".wm[16]" -type "matrix" -0.15032955336689471 -0.91652626290948291 0.37064893738103077 0 -0.18332527405206805 0.39425013086275174 0.90053244150804312 0
		 -0.97149002531073059 0.067427321701818033 -0.22728987441123599 0 -20.778432298928998 78.688075561808745 1.8386786028472044 1;
	setAttr ".wm[17]" -type "matrix" 0.33050489618952245 -0.92234231352135565 0.20012788482074734 0 0.19395230387446644 0.27389266359337322 0.94200069673621467 0
		 -0.92366066139927139 -0.27252057815475272 0.26941328301637191 0 -22.104545605412898 70.603054048974087 5.1083117314407582 1;
	setAttr ".wm[18]" -type "matrix" 0.69709034849633267 -0.71622374581259363 0.03299381710925238 0 0.20429156718695227 0.24252303217334781 0.94839207843683737 0
		 -0.68726268748533137 -0.65437460586396756 0.31537893650467036 0 -21.136174992543033 67.900615441503888 5.6946811459655056 1;
	setAttr ".wm[19]" -type "matrix" 0.85209068004744437 -0.52099675924971278 -0.050038483466035857 0 0.2036349207354981 0.24192985744769444 0.9486847543480319 0
		 -0.48215587939309745 -0.81855502009738812 0.31223931052965381 0 -19.51310888412133 66.233000202844025 5.7715021010296548 1;
	setAttr -s 83 ".xm";
	setAttr ".xm[0]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[1]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[2]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[3]" -type "matrix" "xform" 1 1 1 -3.3306690738754696e-16 -2.7733391199176202e-32 -1.6653345369377348e-16 0 -5.8064397712757788e-15
		 88.867637422588331 0.47329046439253208 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.50758331815289393 0.49229988333626273 0.50758331815289404 0.49229988333626312 1
		 1 1 yes;
	setAttr ".xm[4]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.3816508661516451
		 -3.9968028886505635e-15 -3.7860044429179921e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[5]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.3816508661518583
		 2.6645352591003757e-15 -7.5403910957633697e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[6]" -type "matrix" "xform" 1 1 1 0 0 1.6653345369377348e-16 0 3.3816508661515314
		 -3.5527136788005009e-15 -1.8866786634444164e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.059683120475990684 0.99821737368683805 1
		 1 1 yes;
	setAttr ".xm[7]" -type "matrix" "xform" 1 1 1 0 0 1.8041124150158794e-16 0 11.25221445791739
		 0 -3.5754913018389324e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.043988873638582705 0.99903202100633837 1
		 1 1 yes;
	setAttr ".xm[8]" -type "matrix" "xform" 1 1 1 0 0 5.5511151231257827e-17 0 12.624062549953081
		 7.1054273576010019e-15 -3.6544896322720324e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.0632026167049895 0.99800071605267004 1
		 1 1 yes;
	setAttr ".xm[9]" -type "matrix" "xform" 1 1 1 2.9143354396410389e-16 1.0894063429134349e-15 -4.9960036108132025e-16 2 4.8146220815627032
		 3.4256949883352332 -1.1096741025741677 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.26948490259817925 0.75350381115558429 -0.061863635196684641 0.59647530081798938 1
		 1 1 yes;
	setAttr ".xm[10]" -type "matrix" "xform" 1 1 1 -5.5511151231257827e-17 1.1102230246251565e-16 5.5511151231257827e-17 5 15.749789208862282
		 -7.1054273576010019e-14 1.4210854715202004e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.18770350911157199 0.481247987192779 0.31113934186032988 0.79772180453891406 1
		 1 1 yes;
	setAttr ".xm[11]" -type "matrix" "xform" 1 1 1 0 0 0 5 9.2097755641924266
		 -1.7763568394002505e-14 -3.5527136788005009e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[12]" -type "matrix" "xform" 1 1 1 0 0 0 5 9.2097755641923982
		 -1.7763568394002505e-14 -4.2632564145606011e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[13]" -type "matrix" "xform" 1 1 1 0 0 -5.5511151231257827e-17 5 9.209775564192455
		 -1.0658141036401503e-14 -4.2632564145606011e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.21320677063942034 0.97700709974570277 1
		 1 1 yes;
	setAttr ".xm[14]" -type "matrix" "xform" 1 1 1 0 0 0 5 7.7375150543099949
		 1.4210854715202004e-14 -2.1316282072803006e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[15]" -type "matrix" "xform" 1 1 1 0 0 0 5 7.7375150543100233
		 1.7763568394002505e-14 -3.5527136788005009e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[16]" -type "matrix" "xform" 1 1 1 8.5326710974609209e-16 -3.2612801348363894e-16 1.6445178552260129e-15 5 7.7375150543100233
		 0 -2.1316282072803006e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.25944557362822468 -0.053014952796433527 0.0078260709843837907 0.96426975567921902 1
		 1 1 yes;
	setAttr ".xm[17]" -type "matrix" "xform" 1 1 1 -8.2572837456495988e-16 -1.6653345369377392e-16 1.1379786002407851e-15 5 8.8213746185177726
		 -3.5527136788005009e-14 6.7501559897209518e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.1812447007851864 0.24143719836469685 -0.08237921563482134 0.94977476409645978 1
		 1 1 no;
	setAttr ".xm[18]" -type "matrix" "xform" 1 1 1 -1.5213524884316596e-15 -2.9143354396410448e-16 1.160963686297478e-15 5 2.9299735768954491
		 -2.1316282072803006e-14 5.3290705182007514e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0041471581112458595 0.22568814001148427 -0.016301903414306606 0.97405436834030357 1
		 1 1 no;
	setAttr ".xm[19]" -type "matrix" "xform" 1 1 1 -1.3246341686295321e-15 -1.1067237197618149e-16 3.9020436187753305e-16 5 2.3283439685009455
		 1.7763568394002505e-14 -5.3290705182007514e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.00046031140391202685 0.1313706786620884 7.2721475626286183e-05 0.99133320715734163 1
		 1 1 no;
	setAttr ".xm[20]" -type "matrix" "xform" 1 1 1 2.4980018054066022e-16 3.122502256758246e-17 -5.3429483060085659e-16 5 9.1476653008053574
		 2.8421709430404007e-14 -1.4210854715202004e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.12399361603247876 0.18641910427827277 -0.10029218186111157 0.96944054949275482 1
		 1 1 no;
	setAttr ".xm[21]" -type "matrix" "xform" 1 1 1 -2.191579166407886e-16 1.1106157865236087e-16 1.1099519740820349e-16 5 2.6150711681149517
		 -7.9936057773011271e-15 -3.9968028886505635e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 4.2036359576405627e-05 0.23352034459465523 0.0001740768113844271 0.97235189956651069 1
		 1 1 no;
	setAttr ".xm[22]" -type "matrix" "xform" 1 1 1 -9.2130079606955752e-17 6.5183589862544133e-16 2.6020852139652137e-17 5 2.2798674841392526
		 3.5527136788005009e-15 -2.1316282072803006e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.014226627620729826 0.050664508358947077 -0.0013156844410576322 0.99861352866548858 1
		 1 1 no;
	setAttr ".xm[23]" -type "matrix" "xform" 1 1 1 -3.5041414214731503e-16 1.110223024625157e-16 -3.0531133177191805e-16 5 3.140691814167667
		 0.30982708682666882 -1.5412620499281324 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.71964470762268251 0.061771959998256312 0.16339604061873678 0.67201001008821137 1
		 1 1 no;
	setAttr ".xm[24]" -type "matrix" "xform" 1 1 1 3.0747973611688906e-16 1.3126977803368247e-16 -2.317346618416205e-16 0 2.4600734291950914
		 -2.0467143230970652 -0.085862068640999212 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0018891246558813146 -0.029403862449852505 -0.064087473584031607 0.99750921790762459 1
		 1 1 no;
	setAttr ".xm[25]" -type "matrix" "xform" 1 1 1 0 0 2.2204460492503131e-16 5 10.316790868949965
		 2.4868995751603507e-14 1.8836197044295684e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.17276085650730627 0.98496379956771096 1
		 1 1 yes;
	setAttr ".xm[26]" -type "matrix" "xform" 1 1 1 0 0 0 5 1.2444419780076714
		 5.6843418860808015e-14 -6.8047877108372444e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[27]" -type "matrix" "xform" 1 1 1 0 0 0 5 1.2444419780077425
		 -2.1316282072803006e-14 -8.7390391023495893e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[28]" -type "matrix" "xform" 1 1 1 0 0 0 0 1.2444419780078704
		 -3.5527136788005009e-14 -1.4975951865585851e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[29]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.7333259340233553
		 7.1054273576010019e-14 -3.7024267901522484e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[30]" -type "matrix" "xform" 1 1 1 0 0 -4.9960036108132044e-16 5 3.7333259340227016
		 -4.2632564145606011e-14 -3.5865266942518296e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.14789458303942959 0.98900313058533507 1
		 1 1 yes;
	setAttr ".xm[31]" -type "matrix" "xform" 1 1 1 3.8857805861880469e-16 3.3306690738754691e-16 6.4711246131411092e-32 0 7.1840143228172764
		 7.9495028875399854 -6.6289249529645096 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.327180291614668 -0.91247968200079466 0.2152222281462921 -0.11837769733532902 1
		 1 1 yes;
	setAttr ".xm[32]" -type "matrix" "xform" 1 1 1 -3.6082248300317583e-16 1.9428902930940244e-16 3.3306690738754691e-16 0 7.1840143228173474
		 7.9495028875399996 6.6289249529645238 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.91247968200079443 0.32718029161466866 0.11837769733533099 0.21522222814629144 1
		 1 1 yes;
	setAttr ".xm[33]" -type "matrix" "xform" 1 1 1 2.1684043449710089e-19 6.9388939039072284e-18 7.5231638452626401e-37 2 -7.3216659883416781
		 -2.1522866108679537 8.8414397624647219 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.99834971054101485 0.023498253370694631 -0.028507300338170151 0.043966139000687632 1
		 1 1 yes;
	setAttr ".xm[34]" -type "matrix" "xform" 1 1 1 0 0 0 2 -12.439033508293363
		 1.357914879607236e-05 8.2600593032111647e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[35]" -type "matrix" "xform" 1 1 1 0 0 0 2 -12.43903350829337
		 1.3579148795628271e-05 7.7271522513910895e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[36]" -type "matrix" "xform" 1 1 1 0 0 1.0900276118941941e-06 2 -12.439033508293356
		 1.3579148795628271e-05 8.1712414612411521e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.068935825723658556 0.99762109637466934 1
		 1 1 yes;
	setAttr ".xm[37]" -type "matrix" "xform" 1 1 1 -5.0190243688937202e-08 -1.1406526823831375e-07 -8.8569965119657819e-07 3 -37.335575103759773
		 2.6645352591003757e-15 1.2434497875801753e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.05344350942954252 -0.02486884457531317 0.063298645820076924 0.99625228396560661 1
		 1 1 yes;
	setAttr ".xm[38]" -type "matrix" "xform" 1 1 1 1.2337353361146986e-14 2.4494295480795837e-15 5.3841696726064635e-14 5 -5.724997006951523
		 -11.847151218614595 -1.1723955140041653e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.015417631002365 -0.031034270675095239 0.61378786716892209 0.78871010188418755 1
		 1 1 no;
	setAttr ".xm[39]" -type "matrix" "xform" 1 1 1 3.3306690738754706e-16 -2.2204460492503116e-16 9.4368957093138306e-16 2 4.8146220815627174
		 3.4256949883352359 1.1096741025742167 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.6795119949146271 -0.18589095985181531 0.70255475394123157 0.10062215226822657 1
		 1 1 yes;
	setAttr ".xm[40]" -type "matrix" "xform" 1 1 1 0 -1.3877787807814457e-17 0 2 -7.3216659883418345
		 -2.1522866108679581 -8.8414397624647592 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.023498253370695169 -0.99834971054101485 0.043966139000687576 0.028507300338171695 1
		 1 1 yes;
	setAttr ".xm[41]" -type "matrix" "xform" 1 1 1 0 0 0 2 12.439033508293349
		 -1.358294346929384e-05 -2.1316282072803006e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[42]" -type "matrix" "xform" 1 1 1 0 0 0 2 12.439033508293356
		 -1.3582943469821196e-05 -1.9539925233402755e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[43]" -type "matrix" "xform" 1 1 1 0 0 1.0897223354234247e-06 2 12.439033508293349
		 -1.3582943469279962e-05 -2.3092638912203256e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.068935825723656377 0.99762109637466956 1
		 1 1 yes;
	setAttr ".xm[44]" -type "matrix" "xform" 1 1 1 -5.3461489324973089e-08 -1.2041855584009298e-07 -8.8494812641806198e-07 3 37.335575103759773
		 -2.7533531010703882e-14 -7.1054273576010019e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.053443509429542964 -0.02486884457531369 0.063298645820076826 0.9962522839656065 1
		 1 1 yes;
	setAttr ".xm[45]" -type "matrix" "xform" 1 1 1 6.6613381477509392e-16 -1.110223024625157e-16 -1.6653345369377343e-16 5 -14.409854929115877
		 -4.2632564145606011e-14 -3.836930773104541e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.18172647704095593 0.62214217906890057 0.21351649504947295 0.73097558297625187 1
		 1 1 yes;
	setAttr ".xm[46]" -type "matrix" "xform" 1 1 1 0 0 0 5 -9.536592158706739
		 3.5527136788005009e-15 -2.1316282072803006e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[47]" -type "matrix" "xform" 1 1 1 0 0 0 5 -9.5365921587067533
		 0 -2.1316282072803006e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[48]" -type "matrix" "xform" 1 1 1 0 0 0 5 -9.5365921587067533
		 7.1054273576010019e-15 -2.1316282072803006e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.21119289257827309 0.97744440359767881 1
		 1 1 yes;
	setAttr ".xm[49]" -type "matrix" "xform" 1 1 1 0 0 0 5 -7.5870240637034385
		 -1.0658141036401503e-14 -6.3948846218409017e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[50]" -type "matrix" "xform" 1 1 1 0 0 0 5 -7.5870240637034954
		 -3.5527136788005009e-15 -5.6843418860808015e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[51]" -type "matrix" "xform" 1 1 1 2.6085904270001242e-16 8.7169854667834446e-17 -8.902790614093159e-16 5 -7.5870240637034385
		 -7.1054273576010019e-15 -7.1054273576010019e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.018047855374435502 -0.0025751465101356511 -0.095500552492434596 0.99526242168107315 1
		 1 1 yes;
	setAttr ".xm[52]" -type "matrix" "xform" 1 1 1 5.8286708792820748e-16 3.1571967262777879e-16 -7.0082828429463026e-16 5 -9.1476653008053148
		 -8.8817841970012523e-15 4.9737991503207013e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.12399361603247891 0.18641910427827277 -0.10029218186111151 0.96944054949275482 1
		 1 1 no;
	setAttr ".xm[53]" -type "matrix" "xform" 1 1 1 6.5357062210141804e-16 4.4397208603840854e-16 -4.2555612896413857e-16 5 -2.6150711681148522
		 3.5527136788005009e-14 -5.773159728050814e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 4.2036359576391789e-05 0.23352034459465501 0.0001740768113846492 0.97235189956651069 1
		 1 1 no;
	setAttr ".xm[54]" -type "matrix" "xform" 1 1 1 6.3341801422034393e-16 8.9376883715200361e-16 -2.9121670352960679e-16 5 -2.2798674841393876
		 4.7961634663806763e-14 -1.2434497875801753e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.014226627620729061 0.050664508358947251 -0.0013156844410582849 0.99861352866548858 1
		 1 1 no;
	setAttr ".xm[55]" -type "matrix" "xform" 1 1 1 9.8532293435482643e-16 1.2143064331837069e-17 -1.1796119636642288e-15 5 -8.684292676494465
		 1.9594868983361824 -0.27542882814710623 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.020132332223754872 0.22328320016692141 -0.14005854817278787 0.96442879716761964 1
		 1 1 no;
	setAttr ".xm[56]" -type "matrix" "xform" 1 1 1 8.6649437625041514e-16 6.782226689983072e-16 -1.4289784633358978e-16 5 -2.9299735768952786
		 4.0856207306205761e-14 -1.8318679906315083e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0041471581112478024 0.22568814001148371 -0.016301903414307324 0.97405436834030368 1
		 1 1 no;
	setAttr ".xm[57]" -type "matrix" "xform" 1 1 1 1.1081799811563792e-15 6.1052770320951511e-16 1.1596897487448042e-16 5 -2.3283439685011231
		 1.4210854715202004e-14 -2.2382096176443156e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.00046031140391312319 0.13137067866208801 7.2721475625897619e-05 0.99133320715734163 1
		 1 1 no;
	setAttr ".xm[58]" -type "matrix" "xform" 1 1 1 3.2699537522162819e-16 -1.1831356207248047e-16 -1.2314368275090359e-15 0 -2.4600734291951341
		 2.0467143230970759 0.085862068641070266 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0018891246558813306 -0.029403862449852377 -0.064087473584031704 0.99750921790762459 1
		 1 1 no;
	setAttr ".xm[59]" -type "matrix" "xform" 1 1 1 6.106226635438362e-16 2.3592239273284552e-16 -8.0491169285323859e-16 5 -4.5739933387022518
		 2.4090150870201201 0.41403096061252143 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.22589560753748586 0.20293929865529522 -0.17851742476115592 0.93590509380663811 1
		 1 1 no;
	setAttr ".xm[60]" -type "matrix" "xform" 1 1 1 -5.5511151231257827e-17 -8.3266726846886716e-17 -3.0531133177191795e-16 5 4.5739933387022518
		 -2.4090150870201303 -0.41403096061268485 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.22589560753748572 0.20293929865529542 -0.17851742476115717 0.93590509380663778 1
		 1 1 no;
	setAttr ".xm[61]" -type "matrix" "xform" 1 1 1 1.1898170166127488e-15 1.6326157717676612e-16 -1.3474464599649849e-15 5 -2.0845348094500054
		 4.2632564145606011e-14 -7.1054273576010019e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0022566739606371413 0.1892996968069745 -0.00024193591990506763 0.98191673459536954 1
		 1 1 no;
	setAttr ".xm[62]" -type "matrix" "xform" 1 1 1 2.4036762164003623e-16 -2.2316819412956414e-16 -4.7596475372113635e-16 5 2.0845348094499769
		 -2.1316282072803006e-14 8.8817841970012523e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0022566739606366135 0.18929969680697478 -0.0002419359199037909 0.98191673459536954 1
		 1 1 no;
	setAttr ".xm[63]" -type "matrix" "xform" 1 1 1 1.3138361926179345e-15 4.836761416729393e-16 -4.2847669856627165e-16 5 -1.583329398273662
		 7.1054273576010019e-15 2.8421709430404007e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.018463746298894874 0.1821570841808989 0.0031855123646682137 0.98309091098753298 1
		 1 1 no;
	setAttr ".xm[64]" -type "matrix" "xform" 1 1 1 -4.9049306283244221e-16 1.1923513391909328e-16 2.8275992658421961e-16 5 1.5833293982735626
		 3.907985046680551e-14 -6.9277916736609768e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.018463746298894974 0.18215708418089915 0.0031855123646680212 0.98309091098753298 1
		 1 1 no;
	setAttr ".xm[65]" -type "matrix" "xform" 1 1 1 4.0939474033052657e-16 5.7245874707234624e-16 -2.7755575615628923e-16 5 -5.5343868138587027
		 0.8843439488534206 -0.0059640065208768078 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.069155348334480393 0.24166611535217553 -0.096502991195942592 0.9630691559683352 1
		 1 1 no;
	setAttr ".xm[66]" -type "matrix" "xform" 1 1 1 6.7307270867900125e-16 -8.6736173798846672e-18 -1.8665624601510448e-15 5 5.5343868138587595
		 -0.88434394885342293 0.005964006520713383 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.069155348334480615 0.24166611535217569 -0.096502991195943216 0.96306915596833509 1
		 1 1 no;
	setAttr ".xm[67]" -type "matrix" "xform" 1 1 1 4.4051134268086045e-16 1.1130055278568872e-16 8.8037216405822935e-17 5 -2.5935478552189153
		 3.0198066269804258e-14 3.9523939676655573e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.0024475399071750286 0.23501427832919711 -0.0005203549457172827 0.97198869734197002 1
		 1 1 no;
	setAttr ".xm[68]" -type "matrix" "xform" 1 1 1 -9.4325589006238994e-18 -5.4607367076537495e-17 -4.0527477207508161e-16 5 2.5935478552188158
		 -3.3750779948604759e-14 -6.1728400169158704e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.0024475399071750706 0.23501427832919733 -0.00052035494571706119 0.97198869734197002 1
		 1 1 no;
	setAttr ".xm[69]" -type "matrix" "xform" 1 1 1 1.0400277102202982e-15 1.0989236051087838e-16 -7.4376269032505666e-17 5 -2.1330630437695888
		 3.5527136788005009e-14 -3.907985046680551e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0049259682626423681 0.066731197704196762 0.00041034910141410369 0.99775874524017782 1
		 1 1 no;
	setAttr ".xm[70]" -type "matrix" "xform" 1 1 1 4.8314081685027488e-16 -1.6960394812757044e-16 -5.5435257079183842e-16 5 2.1330630437695959
		 1.9539925233402755e-14 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0049259682626422432 0.066731197704196707 0.00041034910141424268 0.99775874524017782 1
		 1 1 no;
	setAttr ".xm[71]" -type "matrix" "xform" 1 1 1 7.077671781985371e-16 6.9388939039072284e-16 3.1918911957973216e-16 5 -3.1406918141675959
		 -0.30982708682665638 1.5412620499281928 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.71964470762268251 0.061771959998256458 0.16339604061873661 0.67201001008821126 1
		 1 1 no;
	setAttr ".xm[72]" -type "matrix" "xform" 1 1 1 6.9388939039072025e-17 1.0132953504049522e-15 4.9092674370143631e-16 5 -4.0601659831539081
		 1.0658141036401503e-13 -9.2370555648813024e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.017239913876693082 0.13220968231242489 -0.03244861646376325 0.99054049516511922 1
		 1 1 no;
	setAttr ".xm[73]" -type "matrix" "xform" 1 1 1 -2.6541269182445153e-16 3.8510861166685113e-16 1.9862583799934446e-16 5 4.0601659831538512
		 3.907985046680551e-14 1.6697754290362354e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.017239913876693165 0.13220968231242494 -0.032448616463763201 0.99054049516511922 1
		 1 1 no;
	setAttr ".xm[74]" -type "matrix" "xform" 1 1 1 0 0 0 5 -2.1504736042849402
		 -4.9737991503207013e-14 3.1974423109204508e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 no;
	setAttr ".xm[75]" -type "matrix" "xform" 1 1 1 0 0 0 5 2.150473604285196
		 7.1054273576010019e-15 -1.865174681370263e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 no;
	setAttr ".xm[76]" -type "matrix" "xform" 1 1 1 1.5494550087424806e-14 1.0477729794904721e-15 6.2061358656328977e-14 5 5.7249970069516376
		 11.847151218614592 1.0746958878371515e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.015417631002365101 -0.03103427067509509 0.61378786716892175 0.78871010188418766 1
		 1 1 no;
	setAttr ".xm[77]" -type "matrix" "xform" 1 1 1.0000000000000007 3.0322499405141561 0.17485063306656556 -0.83598421280242718 0 1.6148669790486139
		 4.9370587667259107 -0.55956448104940737 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[78]" -type "matrix" "xform" 1 0.99999999999999989 0.99999999999999989 3.0322499405141556 0.1748506330665662 -0.83598421280242718 0 -1.6148669790486849
		 -4.9370587667259116 0.55956448104938605 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[79]" -type "matrix" "xform" 1 1 1 0 0 4.4408920985006262e-16 0 1.0864277183106594
		 2.1380826858833553 -3.6581181725347671e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.91396045264121173 0.4058032663839356 1
		 1 1 no;
	setAttr ".xm[80]" -type "matrix" "xform" 1 1 1 0 0 2.2204460492503131e-16 0 2.9712837014492521
		 -0.030423245074715055 -2.9900100508117715e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.53345912296067188 0.84582584740006062 1
		 1 1 yes;
	setAttr ".xm[81]" -type "matrix" "xform" 1 1 1 0 0 -1.1102230246251565e-16 0 1.5070540673335699
		 1.1368683772161603e-13 -2.1002558495556582e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.19703136998903173 0.98039718443100665 1
		 1 1 yes;
	setAttr ".xm[82]" -type "matrix" "xform" 1 1 1 0 0 -1.1102230246251565e-16 0 1.3849295663430015
		 8.5265128291212022e-14 -2.0349608716317084e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.13456946952645843 0.990904161799398 1
		 1 1 yes;
	setAttr -s 80 ".m";
	setAttr -s 81 ".p";
	setAttr -s 83 ".g[0:82]" yes yes yes yes yes yes yes yes yes yes yes 
		yes yes yes yes yes no no no no no no no no yes no no no no no no no no no no no 
		no no no no no no no no no no no no no no no no no no no no no no yes no no no no 
		no no no no no no no no no no no no no no no no yes no no no;
	setAttr ".bp" yes;
createNode dagPose -n "rig:bindPose3";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000D44";
	setAttr -s 20 ".wm";
	setAttr ".wm[0]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[1]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[2]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[3]" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -5.8064397712757504e-15 88.867637422588331 0.47329046439253697 1;
	setAttr ".wm[4]" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -8.4661282183400888e-15 92.247708493863087 0.57664487251233765 1;
	setAttr ".wm[5]" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -1.4880203318250076e-14 95.62777956513807 0.67999928063214798 1;
	setAttr ".wm[6]" -type "matrix" 3.9022319828289044e-16 0.99605373441152567 -0.088752229069772509 0 -4.5635506035450343e-16 0.088752229069772565 0.99605373441152578 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -3.2620673956841366e-14 99.007850636412726 0.78335368875194566 1;
	setAttr ".wm[7]" -type "matrix" 4.2882324480567274e-16 0.98439830163183939 -0.17595449339062028 0 -4.2029122082625582e-16 0.1759544933906203 0.9843983016318395 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -6.3538155657931891e-14 110.21566086762064 -0.2153054263593237 1;
	setAttr ".wm[8]" -type "matrix" 3.7237652132655529e-16 0.99873090588638569 -0.050364448049781949 0 -4.7103058494541948e-16 0.05036444804978199 0.9987309058863858 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -9.3803574503953694e-14 122.64276660148867 -2.4365659568678506 1;
	setAttr ".wm[9]" -type "matrix" -0.86555019344236128 -0.16717919135475579 -0.47209530882001027 0 -0.4147111464715928 -0.28922999948722544 0.86276339305097827 0
		 -0.28078021230868089 0.94254820851486931 0.18101200789257746 0 -1.1096741025743033 130.16265236880656 2.4663549575535777 1;
	setAttr ".wm[10]" -type "matrix" -0.17960524299256644 -0.98248094674772968 -0.049730734634288815 0 0.28084335038909258 -0.099658096810002053 0.95456549082943365 0
		 -0.94279847752942958 0.15747842080073426 0.29382235747181712 0 -14.741907198981476 127.52961534486117 -4.9690466428543587 1;
	setAttr ".wm[11]" -type "matrix" -0.17960524299256644 -0.98248094674772968 -0.049730734634288815 0 0.28084335038909258 -0.099658096810002053 0.95456549082943365 0
		 -0.94279847752942958 0.15747842080073426 0.29382235747181712 0 -16.396031177095228 118.48118632921928 -5.4270555474785969 1;
	setAttr ".wm[12]" -type "matrix" -0.17960524299256644 -0.98248094674772968 -0.049730734634288815 0 0.28084335038909258 -0.099658096810002053 0.95456549082943365 0
		 -0.94279847752942958 0.15747842080073426 0.29382235747181712 0 -18.050155155208973 109.43275731357741 -5.8850644521028368 1;
	setAttr ".wm[13]" -type "matrix" -0.04627468285217369 -0.93467789007364943 0.35247112723512786 0 0.3301358576330663 0.3187127057234741 0.88850015572047136 0
		 -0.94279847752942958 0.15747842080073426 0.29382235747181712 0 -19.704279133322725 100.38432829793551 -6.3430733567270696 1;
	setAttr ".wm[14]" -type "matrix" -0.04627468285217369 -0.93467789007364943 0.35247112723512786 0 0.3301358576330663 0.3187127057234741 0.88850015572047136 0
		 -0.94279847752942958 0.15747842080073426 0.29382235747181712 0 -20.062330188524818 93.152244052559936 -3.6158227035356463 1;
	setAttr ".wm[15]" -type "matrix" -0.04627468285217369 -0.93467789007364943 0.35247112723512786 0 0.3301358576330663 0.3187127057234741 0.88850015572047136 0
		 -0.94279847752942958 0.15747842080073426 0.29382235747181712 0 -20.420381243726901 85.920159807184348 -0.88857205034421671 1;
	setAttr ".wm[16]" -type "matrix" -0.15032955336689471 -0.91652626290948291 0.37064893738103077 0 -0.18332527405206805 0.39425013086275174 0.90053244150804312 0
		 -0.97149002531073059 0.067427321701818033 -0.22728987441123599 0 -20.778432298928998 78.688075561808745 1.8386786028472044 1;
	setAttr ".wm[17]" -type "matrix" 0.28642002316565029 -0.76122608396439762 0.58180616997589174 0 0.9270923853098868 0.066950750302966849 -0.36880524146803284 0
		 0.24179181009747344 0.64502127571584622 0.72490294139539113 0 -19.587111004626703 76.156016522158581 3.6909927720322351 1;
	setAttr ".wm[18]" -type "matrix" 0.15683342175274784 -0.90667454626885757 0.39159231985508347 0 0.95049019220589448 0.030861243995309956 -0.30921833409334509 0
		 0.26827536663235863 0.42070042876995417 0.86662533824660959 0 -18.424198169675343 73.065312270556817 6.0532223921574273 1;
	setAttr ".wm[19]" -type "matrix" 0.15683342175274784 -0.90667454626885757 0.39159231985508347 0 0.95049019220589448 0.030861243995309956 -0.30921833409334509 0
		 0.26827536663235863 0.42070042876995417 0.86662533824660959 0 -18.086932035926321 71.115532591128513 6.8953313396465701 1;
	setAttr -s 20 ".xm";
	setAttr ".xm[0]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[1]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[2]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[3]" -type "matrix" "xform" 1 1 1 -3.3306690738754696e-16 -2.7733391199176202e-32 -1.6653345369377348e-16 0 -5.8064397712757504e-15
		 88.867637422588331 0.47329046439253697 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.50758331815289393 0.49229988333626273 0.50758331815289404 0.49229988333626312 1
		 1 1 yes;
	setAttr ".xm[4]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.3816508661519578
		 -2.2204460492503131e-15 -3.7860044429179921e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[5]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.3816508661521851
		 4.4408920985006262e-16 -7.5403910957637168e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[6]" -type "matrix" "xform" 1 1 1 0 0 1.6653345369377348e-16 0 3.3816508661518583
		 -2.2204460492503131e-15 -1.8866786634444908e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.059683120475990684 0.99821737368683805 1
		 1 1 yes;
	setAttr ".xm[7]" -type "matrix" "xform" 1 1 1 0 0 1.8041124150158794e-16 0 11.252214457917333
		 1.5987211554602254e-14 -3.5308356814624e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.043988873638582705 0.99903202100633837 1
		 1 1 yes;
	setAttr ".xm[8]" -type "matrix" "xform" 1 1 1 0 0 5.5511151231257827e-17 0 12.624062549953194
		 -1.0658141036401503e-14 -3.5678910311322517e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.0632026167049895 0.99800071605267004 1
		 1 1 yes;
	setAttr ".xm[9]" -type "matrix" "xform" 1 1 1 2.9143354396410389e-16 1.0894063429134349e-15 -4.9960036108132025e-16 2 7.2634094188689744
		 5.2754335424177974 -1.1096741025742098 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.26948490259817925 0.75350381115558429 -0.061863635196684641 0.59647530081798938 1
		 1 1 yes;
	setAttr ".xm[10]" -type "matrix" "xform" 1 1 1 -5.5511151231257827e-17 1.1102230246251565e-16 5.5511151231257827e-17 5 15.749789208862296
		 -4.2632564145606011e-14 5.6843418860808015e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.18770350911157199 0.481247987192779 0.31113934186032988 0.79772180453891406 1
		 1 1 yes;
	setAttr ".xm[11]" -type "matrix" "xform" 1 1 1 0 0 0 5 9.2097755641924266
		 -1.7763568394002505e-14 -3.5527136788005009e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[12]" -type "matrix" "xform" 1 1 1 0 0 0 5 9.2097755641924124
		 -1.7763568394002505e-14 -4.2632564145606011e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[13]" -type "matrix" "xform" 1 1 1 0 0 -5.5511151231257827e-17 5 9.2097755641924408
		 -1.0658141036401503e-14 -3.5527136788005009e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.21320677063942034 0.97700709974570277 1
		 1 1 yes;
	setAttr ".xm[14]" -type "matrix" "xform" 1 1 1 0 0 0 5 7.7375150543100091
		 1.0658141036401503e-14 -2.1316282072803006e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[15]" -type "matrix" "xform" 1 1 1 0 0 0 5 7.7375150543100233
		 1.4210854715202004e-14 -2.8421709430404007e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[16]" -type "matrix" "xform" 1 1 1 8.5326710974609209e-16 -3.2612801348363894e-16 1.6445178552260129e-15 5 7.7375150543100375
		 -3.5527136788005009e-15 -2.1316282072803006e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.25944557362822468 -0.053014952796433527 0.0078260709843837907 0.96426975567921902 1
		 1 1 yes;
	setAttr ".xm[17]" -type "matrix" "xform" 1 1 1 -8.7430063189231137e-16 -1.3877787807814453e-15 -7.9103390504542463e-16 5 2.8281660894920577
		 0.45140509071981683 -1.7490989686736569 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.82190734327391901 0.050527276317958614 0.24962155979122058 0.50951387646235391 1
		 1 1 no;
	setAttr ".xm[18]" -type "matrix" "xform" 1 1 1 -7.7889084071358698e-16 -1.2112706671008052e-15 -9.6537361438109354e-16 5 4.0601659831539649
		 1.9539925233402755e-14 -1.4210854715202004e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.017239913876692835 0.13220968231242552 -0.032448616463763687 0.99054049516511911 1
		 1 1 no;
	setAttr ".xm[19]" -type "matrix" "xform" 1 1 1 0 0 0 5 2.1504736042850681
		 2.1316282072803006e-14 4.2632564145606011e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 no;
	setAttr -s 20 ".m";
	setAttr -s 20 ".p";
	setAttr -s 20 ".g[0:19]" yes yes yes yes yes yes yes yes yes yes yes 
		yes yes yes yes yes yes no no no;
	setAttr ".bp" yes;
createNode dagPose -n "rig:bindPose5";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000D45";
	setAttr -s 24 ".wm";
	setAttr ".wm[0]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[1]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[2]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[3]" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -5.8064397712757504e-15 88.867637422588331 0.47329046439253697 1;
	setAttr ".wm[4]" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -8.4661282183400888e-15 92.247708493863087 0.57664487251233765 1;
	setAttr ".wm[5]" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -1.4880203318250076e-14 95.62777956513807 0.67999928063214798 1;
	setAttr ".wm[6]" -type "matrix" 3.9022319828289044e-16 0.99605373441152567 -0.088752229069772509 0 -4.5635506035450343e-16 0.088752229069772565 0.99605373441152578 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -3.2620673956841366e-14 99.007850636412726 0.78335368875194566 1;
	setAttr ".wm[7]" -type "matrix" 4.2882324480567274e-16 0.98439830163183939 -0.17595449339062028 0 -4.2029122082625582e-16 0.1759544933906203 0.9843983016318395 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -6.3538155657931891e-14 110.21566086762064 -0.2153054263593237 1;
	setAttr ".wm[8]" -type "matrix" 3.7237652132655529e-16 0.99873090588638569 -0.050364448049781949 0 -4.7103058494541948e-16 0.05036444804978199 0.9987309058863858 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -9.3803574503953694e-14 122.64276660148867 -2.4365659568678506 1;
	setAttr ".wm[9]" -type "matrix" -0.86555019344236128 -0.16717919135475579 -0.47209530882001027 0 -0.4147111464715928 -0.28922999948722544 0.86276339305097827 0
		 -0.28078021230868089 0.94254820851486931 0.18101200789257746 0 -1.1096741025743033 130.16265236880656 2.4663549575535777 1;
	setAttr ".wm[10]" -type "matrix" -0.17960524299256644 -0.98248094674772968 -0.049730734634288815 0 0.28084335038909258 -0.099658096810002053 0.95456549082943365 0
		 -0.94279847752942958 0.15747842080073426 0.29382235747181712 0 -14.741907198981476 127.52961534486117 -4.9690466428543587 1;
	setAttr ".wm[11]" -type "matrix" -0.17960524299256644 -0.98248094674772968 -0.049730734634288815 0 0.28084335038909258 -0.099658096810002053 0.95456549082943365 0
		 -0.94279847752942958 0.15747842080073426 0.29382235747181712 0 -16.396031177095228 118.48118632921928 -5.4270555474785969 1;
	setAttr ".wm[12]" -type "matrix" -0.17960524299256644 -0.98248094674772968 -0.049730734634288815 0 0.28084335038909258 -0.099658096810002053 0.95456549082943365 0
		 -0.94279847752942958 0.15747842080073426 0.29382235747181712 0 -18.050155155208973 109.43275731357741 -5.8850644521028368 1;
	setAttr ".wm[13]" -type "matrix" -0.04627468285217369 -0.93467789007364943 0.35247112723512786 0 0.3301358576330663 0.3187127057234741 0.88850015572047136 0
		 -0.94279847752942958 0.15747842080073426 0.29382235747181712 0 -19.704279133322725 100.38432829793551 -6.3430733567270696 1;
	setAttr ".wm[14]" -type "matrix" -0.04627468285217369 -0.93467789007364943 0.35247112723512786 0 0.3301358576330663 0.3187127057234741 0.88850015572047136 0
		 -0.94279847752942958 0.15747842080073426 0.29382235747181712 0 -20.062330188524818 93.152244052559936 -3.6158227035356463 1;
	setAttr ".wm[15]" -type "matrix" -0.04627468285217369 -0.93467789007364943 0.35247112723512786 0 0.3301358576330663 0.3187127057234741 0.88850015572047136 0
		 -0.94279847752942958 0.15747842080073426 0.29382235747181712 0 -20.420381243726901 85.920159807184348 -0.88857205034421671 1;
	setAttr ".wm[16]" -type "matrix" -0.15032955336689471 -0.91652626290948291 0.37064893738103077 0 -0.18332527405206805 0.39425013086275174 0.90053244150804312 0
		 -0.97149002531073059 0.067427321701818033 -0.22728987441123599 0 -20.778432298928998 78.688075561808745 1.8386786028472044 1;
	setAttr ".wm[17]" -type "matrix" -0.17446901833935008 -0.90121819653404145 0.39669424482292803 0 -0.17751023723726064 0.4250596804233186 0.88758908496803723 0
		 -0.96853016334839814 0.084439506833921471 -0.23413520104838817 0 -21.025752283409698 76.704502699292917 1.4549982292084849 1;
	setAttr ".wm[18]" -type "matrix" 0.29025706241906335 -0.94944197527605922 0.11962764437934365 0 -0.25095667358465878 0.045112383549485505 0.9669465449722684 0
		 -0.92345632582119386 -0.31068441936212188 -0.22517461194913196 0 -22.075568403229049 70.546347701864164 1.4254904370074044 1;
	setAttr ".wm[19]" -type "matrix" 0.61265823327286184 -0.76588120598381948 0.19513038595704585 0 -0.25457611738377073 0.042501225955412933 0.96611833967174621 0
		 -0.74822515973520964 -0.64157589115634406 -0.16893633779078673 0 -21.470517452927893 68.567202854848333 1.6748584258886119 1;
	setAttr ".wm[20]" -type "matrix" 0.83657318479064857 -0.48478038804900586 0.25521222904141244 0 -0.28214474162991826 0.018080797690039181 0.95920145408849267 0
		 -0.46961649381151183 -0.87444900372631618 -0.12165232682622681 0 -20.500477661092425 67.35456062582881 1.9838141024709173 1;
	setAttr -s 24 ".xm";
	setAttr ".xm[0]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[1]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[2]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[3]" -type "matrix" "xform" 1 1 1 -3.3306690738754696e-16 -2.7733391199176202e-32 -1.6653345369377348e-16 0 -5.8064397712757504e-15
		 88.867637422588331 0.47329046439253697 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.50758331815289393 0.49229988333626273 0.50758331815289404 0.49229988333626312 1
		 1 1 yes;
	setAttr ".xm[4]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.3816508661519578
		 -2.2204460492503131e-15 -3.7860044429179858e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[5]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.3816508661521851
		 0 -7.5403910957637168e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[6]" -type "matrix" "xform" 1 1 1 0 0 1.6653345369377348e-16 0 3.3816508661518583
		 -2.6645352591003757e-15 -1.8866786634444915e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.059683120475990684 0.99821737368683805 1
		 1 1 yes;
	setAttr ".xm[7]" -type "matrix" "xform" 1 1 1 0 0 1.8041124150158794e-16 0 11.252214457917319
		 1.5987211554602254e-14 -3.5308356814624e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.043988873638582705 0.99903202100633837 1
		 1 1 yes;
	setAttr ".xm[8]" -type "matrix" "xform" 1 1 1 0 0 5.5511151231257827e-17 0 12.624062549953194
		 -1.0658141036401503e-14 -3.5678910311322517e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.0632026167049895 0.99800071605267004 1
		 1 1 yes;
	setAttr ".xm[9]" -type "matrix" "xform" 1 1 1 2.9143354396410389e-16 1.0894063429134349e-15 -4.9960036108132025e-16 2 7.2634094188689602
		 5.2754335424177974 -1.1096741025742098 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.26948490259817925 0.75350381115558429 -0.061863635196684641 0.59647530081798938 1
		 1 1 yes;
	setAttr ".xm[10]" -type "matrix" "xform" 1 1 1 -5.5511151231257827e-17 1.1102230246251565e-16 5.5511151231257827e-17 5 15.749789208862282
		 -7.1054273576010019e-14 1.4210854715202004e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.18770350911157199 0.481247987192779 0.31113934186032988 0.79772180453891406 1
		 1 1 yes;
	setAttr ".xm[11]" -type "matrix" "xform" 1 1 1 0 0 0 5 9.2097755641924266
		 -1.7763568394002505e-14 -3.5527136788005009e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[12]" -type "matrix" "xform" 1 1 1 0 0 0 5 9.2097755641923982
		 -1.7763568394002505e-14 -4.2632564145606011e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[13]" -type "matrix" "xform" 1 1 1 0 0 -5.5511151231257827e-17 5 9.209775564192455
		 -1.0658141036401503e-14 -4.2632564145606011e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.21320677063942034 0.97700709974570277 1
		 1 1 yes;
	setAttr ".xm[14]" -type "matrix" "xform" 1 1 1 0 0 0 5 7.7375150543099949
		 1.4210854715202004e-14 -2.1316282072803006e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[15]" -type "matrix" "xform" 1 1 1 0 0 0 5 7.7375150543100233
		 1.7763568394002505e-14 -3.5527136788005009e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[16]" -type "matrix" "xform" 1 1 1 8.5326710974609209e-16 -3.2612801348363894e-16 1.6445178552260129e-15 5 7.7375150543100233
		 0 -2.1316282072803006e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.25944557362822468 -0.053014952796433527 0.0078260709843837907 0.96426975567921902 1
		 1 1 yes;
	setAttr ".xm[17]" -type "matrix" "xform" 1 1 1 2.1684043449710147e-17 7.9453384518347843e-17 1.5750886821219459e-15 0 1.7129654029128432
		 -1.0822004803207861 0.1937285564015454 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.00015751719127216166 -0.0092862058440482519 0.016959320661085769 0.99981304402976801 1
		 1 1 no;
	setAttr ".xm[18]" -type "matrix" "xform" 1 1 1 -4.9960036108132015e-16 -2.5673907444456775e-16 1.4571677198205178e-15 5 5.7212961572779406
		 -2.457421080998877 0.50369581988417877 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.04902171694336073 0.19275784362167403 -0.19133701872866127 0.96116150060969208 1
		 1 1 no;
	setAttr ".xm[19]" -type "matrix" "xform" 1 1 1 -8.7218643765596404e-16 -5.2838974040907804e-17 1.1085967213664283e-15 5 2.0845348094498917
		 -1.4210854715202004e-14 5.9063864910058328e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0022566739606369179 0.18929969680697525 -0.00024193591990390181 0.98191673459536943 1
		 1 1 no;
	setAttr ".xm[20]" -type "matrix" "xform" 1 1 1 -7.2663229599978507e-16 -2.6324428747948067e-16 5.5250942709861296e-16 5 1.583329398273797
		 -1.0658141036401503e-14 -7.460698725481052e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.018463746298893011 0.18215708418089777 0.0031855123646683521 0.98309091098753321 1
		 1 1 no;
	setAttr ".xm[21]" -type "matrix" "xform" 1 1 1 -9.0899510141184652e-16 -5.6898930012039332e-16 1.2836953722228371e-15 5 6.6032140054002184
		 -0.84065823364264247 0.32572873396436108 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.1093532096124808 0.24171465330833219 -0.11363024935380696 0.95744663995194712 1
		 1 1 no;
	setAttr ".xm[22]" -type "matrix" "xform" 1 1 1 -1.8275311819415659e-15 -3.3816858682886094e-16 1.3843093338294919e-15 5 2.5935478552189011
		 -2.8421709430404007e-14 2.2259971643734389e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.0024475399071760971 0.23501427832919741 -0.00052035494571722729 0.97198869734197002 1
		 1 1 no;
	setAttr ".xm[23]" -type "matrix" "xform" 1 1 1 -9.211449420072624e-16 -5.2393646468888404e-16 5.6302618817172226e-16 5 2.1330630437696954
		 -1.4210854715202004e-14 -3.1974423109204508e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0049259682626403558 0.066731197704196471 0.00041034910141402037 0.99775874524017782 1
		 1 1 no;
	setAttr -s 24 ".m";
	setAttr -s 24 ".p";
	setAttr -s 24 ".g[0:23]" yes yes yes yes yes yes yes yes yes yes yes 
		yes yes yes yes yes yes yes no no no no no no;
	setAttr ".bp" yes;
createNode dagPose -n "rig:bindPose7";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000D46";
	setAttr -s 20 ".wm";
	setAttr ".wm[0]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[1]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[2]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[3]" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -5.8064397712757504e-15 88.867637422588331 0.47329046439253697 1;
	setAttr ".wm[4]" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -8.4661282183400888e-15 92.247708493863087 0.57664487251233765 1;
	setAttr ".wm[5]" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -1.4880203318250076e-14 95.62777956513807 0.67999928063214798 1;
	setAttr ".wm[6]" -type "matrix" 3.9022319828289044e-16 0.99605373441152567 -0.088752229069772509 0 -4.5635506035450343e-16 0.088752229069772565 0.99605373441152578 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -3.2620673956841366e-14 99.007850636412726 0.78335368875194566 1;
	setAttr ".wm[7]" -type "matrix" 4.2882324480567274e-16 0.98439830163183939 -0.17595449339062028 0 -4.2029122082625582e-16 0.1759544933906203 0.9843983016318395 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -6.3538155657931891e-14 110.21566086762064 -0.2153054263593237 1;
	setAttr ".wm[8]" -type "matrix" 3.7237652132655529e-16 0.99873090588638569 -0.050364448049781949 0 -4.7103058494541948e-16 0.05036444804978199 0.9987309058863858 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -9.3803574503953694e-14 122.64276660148867 -2.4365659568678506 1;
	setAttr ".wm[9]" -type "matrix" -0.86555019344236284 0.16717919135475193 0.47209530882000911 0 -0.41471114647159285 0.28922999948722428 -0.86276339305097893 0
		 -0.28078021230867711 -0.94254820851487042 -0.18101200789257851 0 1.109674102574151 130.16265236880659 2.4663549575535759 1;
	setAttr ".wm[10]" -type "matrix" -0.17960524299257014 0.98248094674772901 0.049730734634289037 0 0.28084335038909397 0.099658096810003705 -0.95456549082943343 0
		 -0.94279847752942891 -0.15747842080073782 -0.29382235747181917 0 14.741907198981398 127.52961534486124 -4.9690466428542921 1;
	setAttr ".wm[11]" -type "matrix" -0.17960524299257014 0.98248094674772901 0.049730734634289037 0 0.28084335038909397 0.099658096810003705 -0.95456549082943343 0
		 -0.94279847752942891 -0.15747842080073782 -0.29382235747181917 0 16.396031177095232 118.48118632921934 -5.4270555474785063 1;
	setAttr ".wm[12]" -type "matrix" -0.17960524299257014 0.98248094674772901 0.049730734634289037 0 0.28084335038909397 0.099658096810003705 -0.95456549082943343 0
		 -0.94279847752942891 -0.15747842080073782 -0.29382235747181917 0 18.050155155209048 109.43275731357743 -5.8850644521027204 1;
	setAttr ".wm[13]" -type "matrix" -0.046274682852176188 0.93467789007364932 -0.35247112723512836 0 0.33013585763306913 -0.31871270572347316 -0.88850015572047092 0
		 -0.94279847752942891 -0.15747842080073782 -0.29382235747181917 0 19.704279133322888 100.38432829793548 -6.3430733567269328 1;
	setAttr ".wm[14]" -type "matrix" -0.046274682852176188 0.93467789007364932 -0.35247112723512836 0 0.33013585763306913 -0.31871270572347316 -0.88850015572047092 0
		 -0.94279847752942891 -0.15747842080073782 -0.29382235747181917 0 20.062330188525031 93.152244052560022 -3.6158227035355557 1;
	setAttr ".wm[15]" -type "matrix" -0.046274682852176188 0.93467789007364932 -0.35247112723512836 0 0.33013585763306913 -0.31871270572347316 -0.88850015572047092 0
		 -0.94279847752942891 -0.15747842080073782 -0.29382235747181917 0 20.420381243727167 85.920159807184532 -0.8885720503441612 1;
	setAttr ".wm[16]" -type "matrix" -0.15032955336689768 0.91652626290948314 -0.37064893738102944 0 -0.18332527405206522 -0.39425013086275085 -0.90053244150804457 0
		 -0.97149002531073114 -0.067427321701822501 0.22728987441123422 0 20.778432298929314 78.688075561809072 1.8386786028472324 1;
	setAttr ".wm[17]" -type "matrix" 0.3305048961895195 0.9223423135213572 -0.20012788482074576 0 0.19395230387446905 -0.27389266359337144 -0.942000696736215 0
		 -0.92366066139927239 0.27252057815474939 -0.26941328301637335 0 22.104545605413236 70.6030540489743 5.1083117314408906 1;
	setAttr ".wm[18]" -type "matrix" 0.69709034849633056 0.71622374581259618 -0.032993817109251006 0 0.20429156718695479 -0.24252303217334703 -0.94839207843683737 0
		 -0.68726268748533359 0.65437460586396501 -0.31537893650467169 0 21.136174992543353 67.900615441504058 5.694681145965637 1;
	setAttr ".wm[19]" -type "matrix" 0.85209068004744282 0.52099675924971578 0.050038483466037592 0 0.20363492073550038 -0.24192985744769316 -0.94868475434803212 0
		 -0.48215587939310017 0.81855502009738645 -0.31223931052965415 0 19.513108884121674 66.233000202844039 5.7715021010297205 1;
	setAttr -s 20 ".xm";
	setAttr ".xm[0]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[1]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[2]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[3]" -type "matrix" "xform" 1 1 1 -3.3306690738754696e-16 -2.7733391199176202e-32 -1.6653345369377348e-16 0 -5.8064397712757504e-15
		 88.867637422588331 0.47329046439253697 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.50758331815289393 0.49229988333626273 0.50758331815289404 0.49229988333626312 1
		 1 1 yes;
	setAttr ".xm[4]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.3816508661519578
		 -2.2204460492503131e-15 -3.7860044429179921e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[5]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.3816508661521851
		 4.4408920985006262e-16 -7.5403910957637168e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[6]" -type "matrix" "xform" 1 1 1 0 0 1.6653345369377348e-16 0 3.3816508661518583
		 -2.2204460492503131e-15 -1.8866786634444908e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.059683120475990684 0.99821737368683805 1
		 1 1 yes;
	setAttr ".xm[7]" -type "matrix" "xform" 1 1 1 0 0 1.8041124150158794e-16 0 11.252214457917333
		 1.5987211554602254e-14 -3.5308356814624e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.043988873638582705 0.99903202100633837 1
		 1 1 yes;
	setAttr ".xm[8]" -type "matrix" "xform" 1 1 1 0 0 5.5511151231257827e-17 0 12.624062549953194
		 -1.0658141036401503e-14 -3.5678910311322517e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.0632026167049895 0.99800071605267004 1
		 1 1 yes;
	setAttr ".xm[9]" -type "matrix" "xform" 1 1 1 5.5511151231257837e-16 -4.4408920985006252e-16 2.7755575615628904e-16 2 7.2634094188690028
		 5.2754335424177956 1.1096741025742445 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.75350381115558285 -0.26948490259817914 0.59647530081799116 0.061863635196684807 1
		 1 1 yes;
	setAttr ".xm[10]" -type "matrix" "xform" 1 1 1 -5.5511151231257827e-17 -2.3592239273284576e-16 -6.5481618109166019e-33 5 -15.749789208862319
		 -2.8421709430404007e-14 -5.6843418860808015e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.18770350911157213 0.48124798719277906 0.31113934186033004 0.79772180453891406 1
		 1 1 yes;
	setAttr ".xm[11]" -type "matrix" "xform" 1 1 1 0 0 0 5 -9.209775564192455
		 3.5527136788005009e-15 -1.4210854715202004e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[12]" -type "matrix" "xform" 1 1 1 0 0 0 5 -9.2097755641924692
		 -3.5527136788005009e-15 7.1054273576010019e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[13]" -type "matrix" "xform" 1 1 1 0 0 1.1102230246251565e-16 5 -9.2097755641924977
		 0 -1.4210854715202004e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.2132067706394207 0.97700709974570266 1
		 1 1 yes;
	setAttr ".xm[14]" -type "matrix" "xform" 1 1 1 0 0 0 5 -7.7375150543098812
		 7.1054273576010019e-15 -1.4210854715202004e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[15]" -type "matrix" "xform" 1 1 1 0 0 0 5 -7.7375150543099096
		 -3.5527136788005009e-15 -7.1054273576010019e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[16]" -type "matrix" "xform" 1 1 1 -6.3230670699354609e-16 -2.0296264668928668e-16 8.1532003370909924e-16 5 -7.7375150543098954
		 -3.5527136788005009e-15 -2.1316282072803006e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.25944557362822462 -0.053014952796433701 0.0078260709843826805 0.96426975567921891 1
		 1 1 yes;
	setAttr ".xm[17]" -type "matrix" "xform" 1 1 1 -6.3143934525555739e-16 -6.6960326172704793e-16 1.1657341758564142e-15 5 -8.8213746185179076
		 -2.1316282072803006e-14 -3.5527136788005009e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.18124470078518645 0.24143719836469693 -0.082379215634820951 0.94977476409645989 1
		 1 1 no;
	setAttr ".xm[18]" -type "matrix" "xform" 1 1 1 -5.1174342541315741e-17 -7.2112996997442114e-16 1.9342166757141397e-16 5 -2.9299735768954918
		 2.1316282072803006e-14 9.3258734068513149e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0041471581112455516 0.22568814001148424 -0.016301903414306155 0.97405436834030357 1
		 1 1 no;
	setAttr ".xm[19]" -type "matrix" "xform" 1 1 1 -5.1556862620295841e-16 -8.3237292451969683e-16 5.0629530949641833e-16 5 -2.3283439685010379
		 8.1712414612411521e-14 -3.1974423109204508e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0004603114039122973 0.13137067866208849 7.2721475626230672e-05 0.99133320715734163 1
		 1 1 no;
	setAttr -s 20 ".m";
	setAttr -s 20 ".p";
	setAttr -s 20 ".g[0:19]" yes yes yes yes yes yes yes yes yes yes yes 
		yes yes yes yes yes no no no no;
	setAttr ".bp" yes;
createNode dagPose -n "rig:bindPose10";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000D47";
	setAttr -s 24 ".wm";
	setAttr ".wm[0]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[1]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[2]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[3]" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -5.8064397712757504e-15 88.867637422588331 0.47329046439253697 1;
	setAttr ".wm[4]" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -8.4661282183400888e-15 92.247708493863087 0.57664487251233765 1;
	setAttr ".wm[5]" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -1.4880203318250076e-14 95.62777956513807 0.67999928063214798 1;
	setAttr ".wm[6]" -type "matrix" 3.9022319828289044e-16 0.99605373441152567 -0.088752229069772509 0 -4.5635506035450343e-16 0.088752229069772565 0.99605373441152578 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -3.2620673956841366e-14 99.007850636412726 0.78335368875194566 1;
	setAttr ".wm[7]" -type "matrix" 4.2882324480567274e-16 0.98439830163183939 -0.17595449339062028 0 -4.2029122082625582e-16 0.1759544933906203 0.9843983016318395 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -6.3538155657931891e-14 110.21566086762064 -0.2153054263593237 1;
	setAttr ".wm[8]" -type "matrix" 3.7237652132655529e-16 0.99873090588638569 -0.050364448049781949 0 -4.7103058494541948e-16 0.05036444804978199 0.9987309058863858 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -9.3803574503953694e-14 122.64276660148867 -2.4365659568678506 1;
	setAttr ".wm[9]" -type "matrix" -0.86555019344236284 0.16717919135475193 0.47209530882000911 0 -0.41471114647159285 0.28922999948722428 -0.86276339305097893 0
		 -0.28078021230867711 -0.94254820851487042 -0.18101200789257851 0 1.109674102574151 130.16265236880659 2.4663549575535759 1;
	setAttr ".wm[10]" -type "matrix" -0.17960524299257014 0.98248094674772901 0.049730734634289037 0 0.28084335038909397 0.099658096810003705 -0.95456549082943343 0
		 -0.94279847752942891 -0.15747842080073782 -0.29382235747181917 0 14.741907198981398 127.52961534486124 -4.9690466428542921 1;
	setAttr ".wm[11]" -type "matrix" -0.17960524299257014 0.98248094674772901 0.049730734634289037 0 0.28084335038909397 0.099658096810003705 -0.95456549082943343 0
		 -0.94279847752942891 -0.15747842080073782 -0.29382235747181917 0 16.396031177095232 118.48118632921934 -5.4270555474785063 1;
	setAttr ".wm[12]" -type "matrix" -0.17960524299257014 0.98248094674772901 0.049730734634289037 0 0.28084335038909397 0.099658096810003705 -0.95456549082943343 0
		 -0.94279847752942891 -0.15747842080073782 -0.29382235747181917 0 18.050155155209048 109.43275731357743 -5.8850644521027204 1;
	setAttr ".wm[13]" -type "matrix" -0.046274682852176188 0.93467789007364932 -0.35247112723512836 0 0.33013585763306913 -0.31871270572347316 -0.88850015572047092 0
		 -0.94279847752942891 -0.15747842080073782 -0.29382235747181917 0 19.704279133322888 100.38432829793548 -6.3430733567269328 1;
	setAttr ".wm[14]" -type "matrix" -0.046274682852176188 0.93467789007364932 -0.35247112723512836 0 0.33013585763306913 -0.31871270572347316 -0.88850015572047092 0
		 -0.94279847752942891 -0.15747842080073782 -0.29382235747181917 0 20.062330188525031 93.152244052560022 -3.6158227035355557 1;
	setAttr ".wm[15]" -type "matrix" -0.046274682852176188 0.93467789007364932 -0.35247112723512836 0 0.33013585763306913 -0.31871270572347316 -0.88850015572047092 0
		 -0.94279847752942891 -0.15747842080073782 -0.29382235747181917 0 20.420381243727167 85.920159807184532 -0.8885720503441612 1;
	setAttr ".wm[16]" -type "matrix" -0.15032955336689768 0.91652626290948314 -0.37064893738102944 0 -0.18332527405206522 -0.39425013086275085 -0.90053244150804457 0
		 -0.97149002531073114 -0.067427321701822501 0.22728987441123422 0 20.778432298929314 78.688075561809072 1.8386786028472324 1;
	setAttr ".wm[17]" -type "matrix" 0.28642002316564913 0.76122608396439995 -0.58180616997588974 0 0.92709238530988691 -0.066950750302964296 0.36880524146803495 0
		 0.24179181009747713 -0.64502127571584389 -0.72490294139539224 0 19.587111004626987 76.156016522158708 3.6909927720323719 1;
	setAttr ".wm[18]" -type "matrix" 0.15683342175274573 0.90667454626885891 -0.39159231985508181 0 0.95049019220589448 -0.030861243995307007 0.30921833409334737 0
		 0.26827536663236201 -0.42070042876995178 -0.86662533824661003 0 18.42419816967568 73.065312270556873 6.0532223921574611 1;
	setAttr ".wm[19]" -type "matrix" 0.15683342175274573 0.90667454626885891 -0.39159231985508181 0 0.95049019220589448 -0.030861243995307007 0.30921833409334737 0
		 0.26827536663236201 -0.42070042876995178 -0.86662533824661003 0 18.086932035926619 71.115532591128499 6.8953313396467015 1;
	setAttr -s 25 ".xm";
	setAttr ".xm[0]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[1]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[2]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[3]" -type "matrix" "xform" 1 1 1 -3.3306690738754696e-16 -2.7733391199176202e-32 -1.6653345369377348e-16 0 -5.8064397712757504e-15
		 88.867637422588331 0.47329046439253697 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.50758331815289393 0.49229988333626273 0.50758331815289404 0.49229988333626312 1
		 1 1 yes;
	setAttr ".xm[4]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.3816508661519578
		 -2.2204460492503131e-15 -3.7860044429179858e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[5]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.3816508661521851
		 0 -7.5403910957637168e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[6]" -type "matrix" "xform" 1 1 1 0 0 1.6653345369377348e-16 0 3.3816508661518583
		 -2.6645352591003757e-15 -1.8866786634444915e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.059683120475990684 0.99821737368683805 1
		 1 1 yes;
	setAttr ".xm[7]" -type "matrix" "xform" 1 1 1 0 0 1.8041124150158794e-16 0 11.252214457917319
		 1.5987211554602254e-14 -3.5308356814624e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.043988873638582705 0.99903202100633837 1
		 1 1 yes;
	setAttr ".xm[8]" -type "matrix" "xform" 1 1 1 0 0 5.5511151231257827e-17 0 12.624062549953194
		 -1.0658141036401503e-14 -3.5678910311322517e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.0632026167049895 0.99800071605267004 1
		 1 1 yes;
	setAttr ".xm[9]" -type "matrix" "xform" 1 1 1 5.5511151231257837e-16 -4.4408920985006252e-16 2.7755575615628904e-16 2 7.2634094188689886
		 5.2754335424177956 1.1096741025742445 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.75350381115558285 -0.26948490259817914 0.59647530081799116 0.061863635196684807 1
		 1 1 yes;
	setAttr ".xm[10]" -type "matrix" "xform" 1 1 1 -5.5511151231257827e-17 -2.3592239273284576e-16 -6.5481618109166019e-33 5 -15.749789208862358
		 -9.2370555648813024e-14 1.7053025658242404e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.18770350911157213 0.48124798719277906 0.31113934186033004 0.79772180453891406 1
		 1 1 yes;
	setAttr ".xm[11]" -type "matrix" "xform" 1 1 1 0 0 0 5 -9.2097755641924408
		 3.5527136788005009e-15 -2.1316282072803006e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[12]" -type "matrix" "xform" 1 1 1 0 0 0 5 -9.2097755641924692
		 0 7.1054273576010019e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[13]" -type "matrix" "xform" 1 1 1 0 0 1.1102230246251565e-16 5 -9.2097755641925261
		 0 -7.1054273576010019e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.2132067706394207 0.97700709974570266 1
		 1 1 yes;
	setAttr ".xm[14]" -type "matrix" "xform" 1 1 1 0 0 0 5 -7.7375150543098812
		 7.1054273576010019e-15 -1.4210854715202004e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[15]" -type "matrix" "xform" 1 1 1 0 0 0 5 -7.737515054309938
		 0 -7.1054273576010019e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[16]" -type "matrix" "xform" 1 1 1 -6.3230670699354609e-16 -2.0296264668928668e-16 8.1532003370909924e-16 5 -7.7375150543098954
		 -3.5527136788005009e-15 -1.4210854715202004e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.25944557362822462 -0.053014952796433701 0.0078260709843826805 0.96426975567921891 1
		 1 1 yes;
	setAttr ".xm[17]" -type "matrix" "xform" 1 1 1 -3.295974604355934e-16 -6.6613381477509373e-16 -4.3021142204224816e-16 5 -2.8281660894922709
		 -0.45140509071983814 1.749098968673735 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.82190734327391901 0.050527276317958933 0.24962155979122078 0.50951387646235391 1
		 1 1 no;
	setAttr ".xm[18]" -type "matrix" "xform" 1 1 1 2.9490299091605696e-16 -5.1065922324067269e-16 -9.1333191010178894e-16 5 -4.0601659831539436
		 -5.3290705182007514e-15 1.2789769243681803e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.017239913876692724 0.1322096823124253 -0.032448616463763735 0.99054049516511922 1
		 1 1 no;
	setAttr ".xm[19]" -type "matrix" "xform" 1 1 1 0 0 0 5 -2.1504736042851818
		 -2.8421709430404007e-14 -1.1013412404281553e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 no;
	setAttr ".xm[20]" -type "matrix" "xform" 1 1 1 4.6837533851373668e-17 -6.2796989830360417e-16 -3.8857805861880479e-16 5 -8.8450786292564061
		 -1.7792516805196357 0.9817666272234078 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.31751610774830236 0.19847505219261016 -0.029527688217739892 0.92677898692515959 1
		 1 1 no;
	setAttr ".xm[21]" -type "matrix" "xform" 1 1 1 -4.5299322019159972e-16 -8.3258614190311065e-16 1.3346867556475442e-16 5 -2.615071168114838
		 -3.5527136788005009e-15 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 4.2036359576197467e-05 0.23352034459465446 0.00017407681138464925 0.9723518995665108 1
		 1 1 no;
	setAttr ".xm[22]" -type "matrix" "xform" 1 1 1 -7.324869877312067e-16 -3.6785624459717573e-16 3.8640965427383363e-16 5 -2.2798674841394018
		 2.8421709430404007e-14 3.5527136788005009e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.014226627620728034 0.050664508358945752 -0.0013156844410586177 0.99861352866548869 1
		 1 1 no;
	setAttr ".xm[23]" -type "matrix" "xform" 1 1 1 -6.3143934525555739e-16 -6.6960326172704793e-16 1.1657341758564142e-15 5 -8.8213746185179076
		 -2.1316282072803006e-14 -3.5527136788005009e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.18124470078518645 0.24143719836469693 -0.082379215634820951 0.94977476409645989 1
		 1 1 no;
	setAttr ".xm[24]" -type "matrix" "xform" 1 1 1 -3.5014309160419371e-16 -3.4804668505973912e-16 6.6239204673059795e-16 0 -1.7129654029131842
		 1.0822004803207577 -0.19372855640149567 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.00015751719127216066 -0.0092862058440484341 0.016959320661085887 0.99981304402976801 1
		 1 1 no;
	setAttr -s 24 ".m";
	setAttr -s 24 ".p";
	setAttr -s 25 ".g[0:24]" yes yes yes yes yes yes yes yes yes yes yes 
		yes yes yes yes yes yes no no no no no no no no;
	setAttr ".bp" yes;
createNode dagPose -n "rig:bindPose9";
	rename -uid "4A0ED900-0000-438E-5D3D-B42400000D48";
	setAttr -s 24 ".wm";
	setAttr ".wm[0]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[1]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[2]" -type "matrix" 1 0 0 0 0 1 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".wm[3]" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -5.8064397712757504e-15 88.867637422588331 0.47329046439253697 1;
	setAttr ".wm[4]" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -8.4661282183400888e-15 92.247708493863087 0.57664487251233765 1;
	setAttr ".wm[5]" -type "matrix" 3.3306690738754696e-16 0.99953283324041142 0.030563299468407794 0 -4.9960036108132034e-16 -0.030563299468407745 0.99953283324041142 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -1.4880203318250076e-14 95.62777956513807 0.67999928063214798 1;
	setAttr ".wm[6]" -type "matrix" 3.9022319828289044e-16 0.99605373441152567 -0.088752229069772509 0 -4.5635506035450343e-16 0.088752229069772565 0.99605373441152578 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -3.2620673956841366e-14 99.007850636412726 0.78335368875194566 1;
	setAttr ".wm[7]" -type "matrix" 4.2882324480567274e-16 0.98439830163183939 -0.17595449339062028 0 -4.2029122082625582e-16 0.1759544933906203 0.9843983016318395 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -6.3538155657931891e-14 110.21566086762064 -0.2153054263593237 1;
	setAttr ".wm[8]" -type "matrix" 3.7237652132655529e-16 0.99873090588638569 -0.050364448049781949 0 -4.7103058494541948e-16 0.05036444804978199 0.9987309058863858 0
		 1 -2.7755575615628909e-16 5.5511151231257827e-16 0 -9.3803574503953694e-14 122.64276660148867 -2.4365659568678506 1;
	setAttr ".wm[9]" -type "matrix" -0.86555019344236284 0.16717919135475193 0.47209530882000911 0 -0.41471114647159285 0.28922999948722428 -0.86276339305097893 0
		 -0.28078021230867711 -0.94254820851487042 -0.18101200789257851 0 1.109674102574151 130.16265236880659 2.4663549575535759 1;
	setAttr ".wm[10]" -type "matrix" -0.17960524299257014 0.98248094674772901 0.049730734634289037 0 0.28084335038909397 0.099658096810003705 -0.95456549082943343 0
		 -0.94279847752942891 -0.15747842080073782 -0.29382235747181917 0 14.741907198981398 127.52961534486124 -4.9690466428542921 1;
	setAttr ".wm[11]" -type "matrix" -0.17960524299257014 0.98248094674772901 0.049730734634289037 0 0.28084335038909397 0.099658096810003705 -0.95456549082943343 0
		 -0.94279847752942891 -0.15747842080073782 -0.29382235747181917 0 16.396031177095232 118.48118632921934 -5.4270555474785063 1;
	setAttr ".wm[12]" -type "matrix" -0.17960524299257014 0.98248094674772901 0.049730734634289037 0 0.28084335038909397 0.099658096810003705 -0.95456549082943343 0
		 -0.94279847752942891 -0.15747842080073782 -0.29382235747181917 0 18.050155155209048 109.43275731357743 -5.8850644521027204 1;
	setAttr ".wm[13]" -type "matrix" -0.046274682852176188 0.93467789007364932 -0.35247112723512836 0 0.33013585763306913 -0.31871270572347316 -0.88850015572047092 0
		 -0.94279847752942891 -0.15747842080073782 -0.29382235747181917 0 19.704279133322888 100.38432829793548 -6.3430733567269328 1;
	setAttr ".wm[14]" -type "matrix" -0.046274682852176188 0.93467789007364932 -0.35247112723512836 0 0.33013585763306913 -0.31871270572347316 -0.88850015572047092 0
		 -0.94279847752942891 -0.15747842080073782 -0.29382235747181917 0 20.062330188525031 93.152244052560022 -3.6158227035355557 1;
	setAttr ".wm[15]" -type "matrix" -0.046274682852176188 0.93467789007364932 -0.35247112723512836 0 0.33013585763306913 -0.31871270572347316 -0.88850015572047092 0
		 -0.94279847752942891 -0.15747842080073782 -0.29382235747181917 0 20.420381243727167 85.920159807184532 -0.8885720503441612 1;
	setAttr ".wm[16]" -type "matrix" -0.15032955336689768 0.91652626290948314 -0.37064893738102944 0 -0.18332527405206522 -0.39425013086275085 -0.90053244150804457 0
		 -0.97149002531073114 -0.067427321701822501 0.22728987441123422 0 20.778432298929314 78.688075561809072 1.8386786028472324 1;
	setAttr ".wm[17]" -type "matrix" -0.17446901833935335 0.90121819653404156 -0.39669424482292692 0 -0.17751023723725767 -0.42505968042331793 -0.88758908496803857 0
		 -0.96853016334839859 -0.084439506833926273 0.23413520104838653 0 21.025752283410021 76.704502699292931 1.4549982292086749 1;
	setAttr ".wm[18]" -type "matrix" 0.2902570624190603 0.94944197527606078 -0.11962764437934119 0 -0.25095667358465706 -0.045112383549484408 -0.96694654497226928 0
		 -0.92345632582119574 0.31068441936211794 0.22517461194913094 0 22.075568403229472 70.546347701864448 1.4254904370074857 1;
	setAttr ".wm[19]" -type "matrix" 0.61265823327285962 0.76588120598382237 -0.19513038595704346 0 -0.25457611738376934 -0.042501225955411899 -0.96611833967174687 0
		 -0.74822515973521253 0.64157589115634095 0.16893633779078696 0 21.470517452928267 68.567202854848574 1.67485842588871 1;
	setAttr ".wm[20]" -type "matrix" 0.83657318479064779 0.48478038804900936 -0.2552122290414105 0 -0.28214474162991687 -0.018080797690038824 -0.95920145408849322 0
		 -0.46961649381151527 0.8744490037263144 0.12165232682622729 0 20.500477661092781 67.354560625828768 1.9838141024710354 1;
	setAttr -s 24 ".xm";
	setAttr ".xm[0]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[1]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[2]" -type "matrix" "xform" 1 1 1 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[3]" -type "matrix" "xform" 1 1 1 -3.3306690738754696e-16 -2.7733391199176202e-32 -1.6653345369377348e-16 0 -5.8064397712757504e-15
		 88.867637422588331 0.47329046439253697 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.50758331815289393 0.49229988333626273 0.50758331815289404 0.49229988333626312 1
		 1 1 yes;
	setAttr ".xm[4]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.3816508661519578
		 -2.2204460492503131e-15 -3.7860044429179858e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[5]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.3816508661521851
		 0 -7.5403910957637168e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[6]" -type "matrix" "xform" 1 1 1 0 0 1.6653345369377348e-16 0 3.3816508661518583
		 -2.6645352591003757e-15 -1.8866786634444915e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.059683120475990684 0.99821737368683805 1
		 1 1 yes;
	setAttr ".xm[7]" -type "matrix" "xform" 1 1 1 0 0 1.8041124150158794e-16 0 11.252214457917319
		 1.5987211554602254e-14 -3.5308356814624e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 -0.043988873638582705 0.99903202100633837 1
		 1 1 yes;
	setAttr ".xm[8]" -type "matrix" "xform" 1 1 1 0 0 5.5511151231257827e-17 0 12.624062549953194
		 -1.0658141036401503e-14 -3.5678910311322517e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.0632026167049895 0.99800071605267004 1
		 1 1 yes;
	setAttr ".xm[9]" -type "matrix" "xform" 1 1 1 5.5511151231257837e-16 -4.4408920985006252e-16 2.7755575615628904e-16 2 7.2634094188689886
		 5.2754335424177956 1.1096741025742445 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.75350381115558285 -0.26948490259817914 0.59647530081799116 0.061863635196684807 1
		 1 1 yes;
	setAttr ".xm[10]" -type "matrix" "xform" 1 1 1 -5.5511151231257827e-17 -2.3592239273284576e-16 -6.5481618109166019e-33 5 -15.749789208862358
		 -9.2370555648813024e-14 1.7053025658242404e-13 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.18770350911157213 0.48124798719277906 0.31113934186033004 0.79772180453891406 1
		 1 1 yes;
	setAttr ".xm[11]" -type "matrix" "xform" 1 1 1 0 0 0 5 -9.2097755641924408
		 3.5527136788005009e-15 -2.1316282072803006e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[12]" -type "matrix" "xform" 1 1 1 0 0 0 5 -9.2097755641924692
		 0 7.1054273576010019e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[13]" -type "matrix" "xform" 1 1 1 0 0 1.1102230246251565e-16 5 -9.2097755641925261
		 0 -7.1054273576010019e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0.2132067706394207 0.97700709974570266 1
		 1 1 yes;
	setAttr ".xm[14]" -type "matrix" "xform" 1 1 1 0 0 0 5 -7.7375150543098812
		 7.1054273576010019e-15 -1.4210854715202004e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[15]" -type "matrix" "xform" 1 1 1 0 0 0 5 -7.737515054309938
		 0 -7.1054273576010019e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 1 1 yes;
	setAttr ".xm[16]" -type "matrix" "xform" 1 1 1 -6.3230670699354609e-16 -2.0296264668928668e-16 8.1532003370909924e-16 5 -7.7375150543098954
		 -3.5527136788005009e-15 -1.4210854715202004e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.25944557362822462 -0.053014952796433701 0.0078260709843826805 0.96426975567921891 1
		 1 1 yes;
	setAttr ".xm[17]" -type "matrix" "xform" 1 1 1 -3.5014309160419371e-16 -3.4804668505973912e-16 6.6239204673059795e-16 0 -1.7129654029131984
		 1.0822004803207577 -0.19372855640149211 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.00015751719127216066 -0.0092862058440484341 0.016959320661085887 0.99981304402976801 1
		 1 1 no;
	setAttr ".xm[18]" -type "matrix" "xform" 1 1 1 -1.5265566588595912e-16 -4.0939474033052642e-16 -4.3021142204224821e-16 5 -5.7212961572776777
		 2.4574210809988486 -0.50369581988429246 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.049021716943360681 0.19275784362167431 -0.19133701872866152 0.96116150060969197 1
		 1 1 no;
	setAttr ".xm[19]" -type "matrix" "xform" 1 1 1 -5.5372915454265915e-16 1.1162856629451285e-16 2.2139408362153998e-16 5 -2.0845348094499485
		 8.8817841970012523e-15 -1.4654943925052066e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.002256673960637071 0.18929969680697523 -0.00024193591990379079 0.98191673459536943 1
		 1 1 no;
	setAttr ".xm[20]" -type "matrix" "xform" 1 1 1 -8.5782075887053111e-16 3.4180828740321124e-16 1.7433970933566926e-16 5 -1.5833293982740244
		 5.3290705182007514e-15 -7.815970093361102e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.018463746298892757 0.18215708418089793 0.003185512364668493 0.98309091098753321 1
		 1 1 no;
	setAttr ".xm[21]" -type "matrix" "xform" 1 1 1 -8.5348395018058909e-16 -6.8001160258290878e-16 6.3143934525555768e-16 5 -6.6032140054000905
		 0.8406582336426851 -0.3257287339644499 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.10935320961248077 0.24171465330833253 -0.11363024935380669 0.95744663995194712 1
		 1 1 no;
	setAttr ".xm[22]" -type "matrix" "xform" 1 1 1 -5.8969756161486586e-16 1.6574825415166872e-16 6.5702651652621618e-17 5 -2.5935478552191995
		 3.907985046680551e-14 7.4384942649885488e-15 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 -0.0024475399071762086 0.23501427832919741 -0.0005203549457172274 0.97198869734197002 1
		 1 1 no;
	setAttr ".xm[23]" -type "matrix" "xform" 1 1 1 -8.6354670159397018e-16 -1.0954931216724051e-16 1.714123634699582e-16 5 -2.1330630437694396
		 1.7763568394002505e-14 4.9737991503207013e-14 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 1 0.0049259682626402396 0.066731197704196596 0.00041034910141424263 0.99775874524017782 1
		 1 1 no;
	setAttr -s 24 ".m";
	setAttr -s 24 ".p";
	setAttr -s 24 ".g[0:23]" yes yes yes yes yes yes yes yes yes yes yes 
		yes yes yes yes yes yes yes no no no no no no;
	setAttr ".bp" yes;
createNode displayLayer -n "rig:jointLayer";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000D9F";
createNode unitConversion -n "rig:LegLockUnitConversion";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DA0";
	setAttr ".cf" 0.1;
createNode reverse -n "rig:LegLockReverse";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DA1";
createNode multiplyDivide -n "rig:InbetweenUnTwistDividerNeck1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DA4";
	setAttr ".i2" -type "float3" 0.33333334 1 1 ;
createNode unitConversion -n "rig:unitConversion1";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DA5";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion2";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DA6";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:InbetweenUnTwistDividerNeck2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DA7";
	setAttr ".i2" -type "float3" 0.66666669 1 1 ;
createNode unitConversion -n "rig:unitConversion3";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DA8";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion4";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DA9";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:IKCurveInfoNormalizeSpine_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DAE";
	setAttr ".op" 2;
	setAttr ".i2" -type "float3" 33.900246 1 1 ;
createNode multiplyDivide -n "rig:IKCurveInfoAllMultiplySpine_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DAF";
	setAttr ".op" 2;
createNode condition -n "rig:FKIKBlendLegCondition_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DCC";
createNode setRange -n "rig:FKIKBlendLegsetRange_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DCD";
	setAttr ".n" -type "float3" 10 0 0 ;
	setAttr ".om" -type "float3" 10 0 0 ;
createNode unitConversion -n "rig:FKIKBlendSpineUnitConversion_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DD2";
	setAttr ".cf" 0.1;
createNode reverse -n "rig:FKIKBlendSpineReverse_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DD3";
createNode condition -n "rig:FKIKBlendSpineCondition_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DD4";
createNode setRange -n "rig:FKIKBlendSpinesetRange_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DD5";
	setAttr ".n" -type "float3" 10 0 0 ;
	setAttr ".om" -type "float3" 10 0 0 ;
createNode condition -n "rig:FKIKBlendLegCondition_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DD8";
createNode setRange -n "rig:FKIKBlendLegsetRange_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DD9";
	setAttr ".n" -type "float3" 10 0 0 ;
	setAttr ".om" -type "float3" 10 0 0 ;
createNode unitConversion -n "rig:FKIKBlendArmUnitConversion_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DDA";
	setAttr ".cf" 0.1;
createNode reverse -n "rig:FKIKBlendArmReverse_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DDB";
createNode condition -n "rig:FKIKBlendArmCondition_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DDC";
createNode setRange -n "rig:FKIKBlendArmsetRange_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DDD";
	setAttr ".n" -type "float3" 10 0 0 ;
	setAttr ".om" -type "float3" 10 0 0 ;
createNode blendColors -n "rig:ScaleBlendAnkle_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DFE";
createNode blendColors -n "rig:ScaleBlendKnee_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000DFF";
createNode blendColors -n "rig:ScaleBlendHip_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E00";
createNode blendColors -n "rig:ScaleBlendWrist_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E01";
createNode blendColors -n "rig:ScaleBlendElbow_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E02";
createNode blendColors -n "rig:ScaleBlendShoulder_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E03";
createNode blendColors -n "rig:ScaleBlendChest_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E04";
createNode blendColors -n "rig:ScaleBlendSpine2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E05";
createNode blendColors -n "rig:ScaleBlendSpine1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E06";
createNode blendColors -n "rig:ScaleBlendRootPart2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E07";
createNode blendColors -n "rig:ScaleBlendRootPart1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E08";
createNode blendColors -n "rig:ScaleBlendRoot_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E09";
createNode blendColors -n "rig:ScaleBlendAnkle_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E0A";
createNode blendColors -n "rig:ScaleBlendKnee_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E0B";
createNode blendColors -n "rig:ScaleBlendHip_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E0C";
createNode blendColors -n "rig:ScaleBlendWrist_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E0D";
createNode blendColors -n "rig:ScaleBlendElbow_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E0E";
createNode blendColors -n "rig:ScaleBlendShoulder_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E0F";
createNode multiplyDivide -n "rig:IKScaleRootMultiplyDivide_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E10";
createNode multiplyDivide -n "rig:IKScaleRootPart1MultiplyDivide_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E11";
createNode multiplyDivide -n "rig:IKScaleRootPart2MultiplyDivide_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E12";
createNode multiplyDivide -n "rig:IKScaleSpine1MultiplyDivide_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E13";
createNode multiplyDivide -n "rig:IKScaleSpine2MultiplyDivide_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E14";
createNode multiplyDivide -n "rig:IKScaleChestMultiplyDivide_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E15";
createNode setRange -n "rig:IKSetRangeStretchLeg_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E16";
	setAttr ".m" -type "float3" 1 0 0 ;
	setAttr ".om" -type "float3" 10 0 0 ;
createNode setRange -n "rig:IKSetRangeAntiPopLeg_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E17";
	setAttr ".m" -type "float3" 1 0 0 ;
	setAttr ".om" -type "float3" 10 0 0 ;
createNode multiplyDivide -n "rig:IKmessureDivLeg_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E18";
	setAttr ".op" 2;
	setAttr ".i2" -type "float3" 74.652679 1 1 ;
createNode blendTwoAttr -n "rig:IKmessureBlendAntiPopLeg_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E19";
createNode clamp -n "rig:IKdistanceClampLeg_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E1C";
	setAttr ".mx" -type "float3" 74.652679 0 0 ;
createNode blendTwoAttr -n "rig:IKmessureBlendStretchLeg_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E1D";
	setAttr -s 2 ".i";
	setAttr -s 2 ".i";
createNode setRange -n "rig:IKSetRangeStretchArm_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E2B";
	setAttr ".m" -type "float3" 1 0 0 ;
	setAttr ".om" -type "float3" 10 0 0 ;
createNode setRange -n "rig:IKSetRangeAntiPopArm_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E2C";
	setAttr ".m" -type "float3" 1 0 0 ;
	setAttr ".om" -type "float3" 10 0 0 ;
createNode multiplyDivide -n "rig:IKmessureDivArm_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E2D";
	setAttr ".op" 2;
	setAttr ".i2" -type "float3" 51.37085 1 1 ;
createNode blendTwoAttr -n "rig:IKmessureBlendAntiPopArm_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E2E";
createNode clamp -n "rig:IKdistanceClampArm_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E31";
	setAttr ".mx" -type "float3" 51.37085 0 0 ;
createNode blendTwoAttr -n "rig:IKmessureBlendStretchArm_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E32";
	setAttr -s 2 ".i";
	setAttr -s 2 ".i";
createNode setRange -n "rig:IKSetRangeStretchLeg_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E40";
	setAttr ".m" -type "float3" 1 0 0 ;
	setAttr ".om" -type "float3" 10 0 0 ;
createNode setRange -n "rig:IKSetRangeAntiPopLeg_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E41";
	setAttr ".m" -type "float3" 1 0 0 ;
	setAttr ".om" -type "float3" 10 0 0 ;
createNode multiplyDivide -n "rig:IKmessureDivLeg_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E42";
	setAttr ".op" 2;
	setAttr ".i2" -type "float3" 74.652679 1 1 ;
createNode blendTwoAttr -n "rig:IKmessureBlendAntiPopLeg_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E43";
createNode clamp -n "rig:IKdistanceClampLeg_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E46";
	setAttr ".mx" -type "float3" 74.652679 0 0 ;
createNode blendTwoAttr -n "rig:IKmessureBlendStretchLeg_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E47";
	setAttr -s 2 ".i";
	setAttr -s 2 ".i";
createNode setRange -n "rig:IKSetRangeStretchArm_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E55";
	setAttr ".m" -type "float3" 1 0 0 ;
	setAttr ".om" -type "float3" 10 0 0 ;
createNode setRange -n "rig:IKSetRangeAntiPopArm_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E56";
	setAttr ".m" -type "float3" 1 0 0 ;
	setAttr ".om" -type "float3" 10 0 0 ;
createNode multiplyDivide -n "rig:IKmessureDivArm_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E57";
	setAttr ".op" 2;
	setAttr ".i2" -type "float3" 51.37085 1 1 ;
createNode blendTwoAttr -n "rig:IKmessureBlendAntiPopArm_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E58";
createNode clamp -n "rig:IKdistanceClampArm_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E5B";
	setAttr ".mx" -type "float3" 51.37085 0 0 ;
createNode blendTwoAttr -n "rig:IKmessureBlendStretchArm_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E5C";
	setAttr -s 2 ".i";
	setAttr -s 2 ".i";
createNode unitConversion -n "rig:HipSwingerStabilizerUnitConversion";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E6A";
	setAttr ".cf" 0.1;
createNode reverse -n "rig:HipSwingerStabilizerReverse";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E6B";
createNode unitConversion -n "rig:CenterBtwLegsUnitConversion";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E6C";
	setAttr ".cf" 0.1;
createNode reverse -n "rig:CenterBtwLegsUnitReverse";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E6D";
createNode multiplyDivide -n "rig:twistAmountDivideKneePart0_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E6F";
createNode plusMinusAverage -n "rig:twistAdditionKneePart0_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E70";
createNode unitConversion -n "rig:unitConversion30";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E71";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion31";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E72";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideKneePart1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E73";
createNode plusMinusAverage -n "rig:twistAdditionKneePart1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E74";
createNode unitConversion -n "rig:unitConversion32";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E75";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion33";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E76";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideKneePart2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E77";
createNode plusMinusAverage -n "rig:twistAdditionKneePart2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E78";
createNode unitConversion -n "rig:unitConversion34";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E79";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion35";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E7A";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideHipPart0_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E7B";
createNode plusMinusAverage -n "rig:twistAdditionHipPart0_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E7C";
	setAttr -s 3 ".i1";
	setAttr -s 3 ".i1";
createNode unitConversion -n "rig:unitConversion36";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E7D";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion37";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E7E";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideHipPart1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E7F";
createNode plusMinusAverage -n "rig:twistAdditionHipPart1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E80";
	setAttr -s 3 ".i1";
	setAttr -s 3 ".i1";
createNode unitConversion -n "rig:unitConversion38";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E81";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion39";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E82";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideHipPart2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E83";
createNode plusMinusAverage -n "rig:twistAdditionHipPart2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E84";
	setAttr -s 3 ".i1";
	setAttr -s 3 ".i1";
createNode unitConversion -n "rig:unitConversion40";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E85";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion41";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E86";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideWristPart0_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E87";
createNode plusMinusAverage -n "rig:twistAdditionWristPart0_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E88";
createNode unitConversion -n "rig:unitConversion42";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E89";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion43";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E8A";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideWristPart1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E8B";
createNode plusMinusAverage -n "rig:twistAdditionWristPart1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E8C";
createNode unitConversion -n "rig:unitConversion44";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E8D";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion45";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E8E";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideWristPart2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E8F";
createNode plusMinusAverage -n "rig:twistAdditionWristPart2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E90";
createNode unitConversion -n "rig:unitConversion46";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E91";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion47";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E92";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideElbowPart0_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E93";
createNode plusMinusAverage -n "rig:twistAdditionElbowPart0_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E94";
	setAttr -s 3 ".i1";
	setAttr -s 3 ".i1";
createNode unitConversion -n "rig:unitConversion48";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E95";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion49";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E96";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideElbowPart1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E97";
createNode plusMinusAverage -n "rig:twistAdditionElbowPart1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E98";
	setAttr -s 3 ".i1";
	setAttr -s 3 ".i1";
createNode unitConversion -n "rig:unitConversion50";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E99";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion51";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E9A";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideElbowPart2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E9B";
createNode plusMinusAverage -n "rig:twistAdditionElbowPart2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E9C";
	setAttr -s 3 ".i1";
	setAttr -s 3 ".i1";
createNode unitConversion -n "rig:unitConversion52";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E9D";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion53";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E9E";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideShoulderPart0_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000E9F";
createNode plusMinusAverage -n "rig:twistAdditionShoulderPart0_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EA0";
	setAttr -s 2 ".i1";
	setAttr -s 2 ".i1";
createNode unitConversion -n "rig:unitConversion54";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EA1";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion55";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EA2";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideShoulderPart1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EA3";
createNode plusMinusAverage -n "rig:twistAdditionShoulderPart1_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EA4";
	setAttr -s 2 ".i1";
	setAttr -s 2 ".i1";
createNode unitConversion -n "rig:unitConversion56";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EA5";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion57";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EA6";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideShoulderPart2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EA7";
createNode plusMinusAverage -n "rig:twistAdditionShoulderPart2_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EA8";
	setAttr -s 2 ".i1";
	setAttr -s 2 ".i1";
createNode unitConversion -n "rig:unitConversion58";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EA9";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion59";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EAA";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideKneePart0_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EAB";
createNode plusMinusAverage -n "rig:twistAdditionKneePart0_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EAC";
createNode unitConversion -n "rig:unitConversion60";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EAD";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion61";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EAE";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideKneePart1_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EAF";
createNode plusMinusAverage -n "rig:twistAdditionKneePart1_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EB0";
createNode unitConversion -n "rig:unitConversion62";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EB1";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion63";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EB2";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideKneePart2_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EB3";
createNode plusMinusAverage -n "rig:twistAdditionKneePart2_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EB4";
createNode unitConversion -n "rig:unitConversion64";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EB5";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion65";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EB6";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideHipPart0_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EB7";
createNode plusMinusAverage -n "rig:twistAdditionHipPart0_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EB8";
	setAttr -s 3 ".i1";
	setAttr -s 3 ".i1";
createNode unitConversion -n "rig:unitConversion66";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EB9";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion67";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EBA";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideHipPart1_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EBB";
createNode plusMinusAverage -n "rig:twistAdditionHipPart1_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EBC";
	setAttr -s 3 ".i1";
	setAttr -s 3 ".i1";
createNode unitConversion -n "rig:unitConversion68";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EBD";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion69";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EBE";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideHipPart2_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EBF";
createNode plusMinusAverage -n "rig:twistAdditionHipPart2_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EC0";
	setAttr -s 3 ".i1";
	setAttr -s 3 ".i1";
createNode unitConversion -n "rig:unitConversion70";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EC1";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion71";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EC2";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideWristPart0_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EC3";
createNode plusMinusAverage -n "rig:twistAdditionWristPart0_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EC4";
createNode unitConversion -n "rig:unitConversion72";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EC5";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion73";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EC6";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideWristPart1_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EC7";
createNode plusMinusAverage -n "rig:twistAdditionWristPart1_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EC8";
createNode unitConversion -n "rig:unitConversion74";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EC9";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion75";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000ECA";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideWristPart2_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000ECB";
createNode plusMinusAverage -n "rig:twistAdditionWristPart2_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000ECC";
createNode unitConversion -n "rig:unitConversion76";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000ECD";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion77";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000ECE";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideElbowPart0_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000ECF";
createNode plusMinusAverage -n "rig:twistAdditionElbowPart0_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000ED0";
	setAttr -s 3 ".i1";
	setAttr -s 3 ".i1";
createNode unitConversion -n "rig:unitConversion78";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000ED1";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion79";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000ED2";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideElbowPart1_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000ED3";
createNode plusMinusAverage -n "rig:twistAdditionElbowPart1_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000ED4";
	setAttr -s 3 ".i1";
	setAttr -s 3 ".i1";
createNode unitConversion -n "rig:unitConversion80";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000ED5";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion81";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000ED6";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideElbowPart2_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000ED7";
createNode plusMinusAverage -n "rig:twistAdditionElbowPart2_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000ED8";
	setAttr -s 3 ".i1";
	setAttr -s 3 ".i1";
createNode unitConversion -n "rig:unitConversion82";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000ED9";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion83";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EDA";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideShoulderPart0_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EDB";
createNode plusMinusAverage -n "rig:twistAdditionShoulderPart0_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EDC";
	setAttr -s 2 ".i1";
	setAttr -s 2 ".i1";
createNode unitConversion -n "rig:unitConversion84";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EDD";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion85";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EDE";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideShoulderPart1_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EDF";
createNode plusMinusAverage -n "rig:twistAdditionShoulderPart1_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EE0";
	setAttr -s 2 ".i1";
	setAttr -s 2 ".i1";
createNode unitConversion -n "rig:unitConversion86";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EE1";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion87";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EE2";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:twistAmountDivideShoulderPart2_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EE3";
createNode plusMinusAverage -n "rig:twistAdditionShoulderPart2_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EE4";
	setAttr -s 2 ".i1";
	setAttr -s 2 ".i1";
createNode unitConversion -n "rig:unitConversion88";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EE5";
	setAttr ".cf" 57.295779513082323;
createNode unitConversion -n "rig:unitConversion89";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EE6";
	setAttr ".cf" 0.017453292519943295;
createNode multiplyDivide -n "rig:multWithStretchyLeg_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EE8";
createNode multiplyDivide -n "rig:volume1OverLeg_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EE9";
	setAttr ".op" 2;
	setAttr ".i1" -type "float3" 1 0 0 ;
createNode multiplyDivide -n "rig:volumepowLeg_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EEA";
	setAttr ".op" 3;
	setAttr ".i2" -type "float3" 0.5 1 1 ;
createNode blendTwoAttr -n "rig:volumeBlendLegBlendTwo_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EEB";
	setAttr -s 2 ".i[0:1]"  1 1;
createNode multiplyDivide -n "rig:multWithStretchyArm_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EED";
createNode multiplyDivide -n "rig:volume1OverArm_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EEE";
	setAttr ".op" 2;
	setAttr ".i1" -type "float3" 1 0 0 ;
createNode multiplyDivide -n "rig:volumepowArm_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EEF";
	setAttr ".op" 3;
	setAttr ".i2" -type "float3" 0.5 1 1 ;
createNode blendTwoAttr -n "rig:volumeBlendArmBlendTwo_R";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EF0";
	setAttr -s 2 ".i[0:1]"  1 1;
createNode multiplyDivide -n "rig:multWithStretchySpine_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EF2";
createNode multiplyDivide -n "rig:volume1OverSpine_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EF3";
	setAttr ".op" 2;
	setAttr ".i1" -type "float3" 1 0 0 ;
createNode multiplyDivide -n "rig:volumepowSpine_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EF4";
	setAttr ".op" 3;
	setAttr ".i2" -type "float3" 0.5 1 1 ;
createNode blendTwoAttr -n "rig:volumeBlendSpineBlendTwo_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EF5";
	setAttr -s 2 ".i[0:1]"  1 316.22775268554688;
createNode multiplyDivide -n "rig:multWithStretchyLeg_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EF7";
createNode multiplyDivide -n "rig:volume1OverLeg_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EF8";
	setAttr ".op" 2;
	setAttr ".i1" -type "float3" 1 0 0 ;
createNode multiplyDivide -n "rig:volumepowLeg_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EF9";
	setAttr ".op" 3;
	setAttr ".i2" -type "float3" 0.5 1 1 ;
createNode blendTwoAttr -n "rig:volumeBlendLegBlendTwo_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EFA";
	setAttr -s 2 ".i[0:1]"  1 1;
createNode multiplyDivide -n "rig:multWithStretchyArm_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EFC";
createNode multiplyDivide -n "rig:volume1OverArm_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EFD";
	setAttr ".op" 2;
	setAttr ".i1" -type "float3" 1 0 0 ;
createNode multiplyDivide -n "rig:volumepowArm_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EFE";
	setAttr ".op" 3;
	setAttr ".i2" -type "float3" 0.5 1 1 ;
createNode blendTwoAttr -n "rig:volumeBlendArmBlendTwo_L";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000EFF";
	setAttr -s 2 ".i[0:1]"  1 1;
createNode plusMinusAverage -n "rig:IKSquashDistributNormalizerASpine2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F00";
	setAttr -s 2 ".i1[1]"  -1;
createNode plusMinusAverage -n "rig:IKSquashDistributNormalizerBSpine2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F01";
	setAttr -s 2 ".i1[1]"  1;
createNode multiplyDivide -n "rig:IKSquashDistributerSpine2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F02";
createNode plusMinusAverage -n "rig:IKSquashDistributNormalizerASpine1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F03";
	setAttr -s 2 ".i1[1]"  -1;
createNode plusMinusAverage -n "rig:IKSquashDistributNormalizerBSpine1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F04";
	setAttr -s 2 ".i1[1]"  1;
createNode multiplyDivide -n "rig:IKSquashDistributerSpine1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F05";
createNode plusMinusAverage -n "rig:IKSquashDistributNormalizerARootPart2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F06";
	setAttr -s 2 ".i1[1]"  -1;
createNode plusMinusAverage -n "rig:IKSquashDistributNormalizerBRootPart2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F07";
	setAttr -s 2 ".i1[1]"  1;
createNode multiplyDivide -n "rig:IKSquashDistributerRootPart2_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F08";
createNode plusMinusAverage -n "rig:IKSquashDistributNormalizerARootPart1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F09";
	setAttr -s 2 ".i1[1]"  -1;
createNode plusMinusAverage -n "rig:IKSquashDistributNormalizerBRootPart1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F0A";
	setAttr -s 2 ".i1[1]"  1;
createNode multiplyDivide -n "rig:IKSquashDistributerRootPart1_M";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F0B";
createNode displayLayer -n "rig:Geo";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F0D";
	setAttr ".dt" 2;
	setAttr ".do" 1;
createNode renderLayerManager -n "rig:renderLayerManager1";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F10";
createNode renderLayer -n "rig:defaultRenderLayer1";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F11";
	setAttr ".g" yes;
createNode shadingEngine -n "rig:eyes_defaultMat";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F12";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:eyes_materialInfo1";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F13";
createNode lambert -n "rig:eyes_white";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F14";
	setAttr ".c" -type "float3" 0.80000001 0.80000001 0.80000001 ;
	setAttr ".ambc" -type "float3" 0.40000001 0.40000001 0.40000001 ;
createNode lambert -n "rig:body_mtl";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F15";
createNode shadingEngine -n "rig:lambert2SG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F16";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo3";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F17";
createNode lambert -n "rig:bikini_mtl";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F18";
	setAttr ".c" -type "float3" 0.36708629 0.36708629 0.36708629 ;
createNode shadingEngine -n "rig:lambert3SG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F19";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo4";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F1A";
createNode blinn -n "rig:eye_blue";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F1D";
	setAttr ".c" -type "float3" 0.192552 0.76171041 0.90399998 ;
createNode shadingEngine -n "rig:blinn2SG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F1E";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo5";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F1F";
createNode surfaceShader -n "rig:iris_mtl";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F20";
createNode shadingEngine -n "rig:surfaceShader1SG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F21";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo6";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F22";
createNode blinn -n "rig:eye_black";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F23";
	setAttr ".c" -type "float3" 0.044296939 0.044296939 0.044296939 ;
createNode shadingEngine -n "rig:blinn3SG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F24";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo7";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F25";
createNode blinn -n "rig:teeth_mtl";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F26";
	setAttr ".c" -type "float3" 0.54430455 0.54430455 0.54430455 ;
createNode shadingEngine -n "rig:blinn4SG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F27";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo8";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F28";
createNode blinn -n "rig:gum_mtl";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F29";
	setAttr ".c" -type "float3" 0.94400001 0.51447994 0.51447994 ;
createNode shadingEngine -n "rig:blinn5SG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F2A";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo9";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F2B";
createNode blinn -n "rig:lens_mtl";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F2C";
	setAttr ".c" -type "float3" 0 0 0 ;
	setAttr ".it" -type "float3" 0.90505838 0.90505838 0.90505838 ;
createNode shadingEngine -n "rig:blinn6SG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F2D";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo10";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F2E";
createNode lambert -n "rig:asRed";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F31";
	setAttr ".c" -type "float3" 1 0 0 ;
createNode shadingEngine -n "rig:asRedSG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F32";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo11";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F33";
createNode lambert -n "rig:asRed2";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F34";
	setAttr ".c" -type "float3" 1 0 1 ;
createNode shadingEngine -n "rig:asRed2SG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F35";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo12";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F36";
createNode lambert -n "rig:asGreen";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F37";
	setAttr ".c" -type "float3" 0 1 0 ;
createNode shadingEngine -n "rig:asGreenSG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F38";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo13";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F39";
createNode lambert -n "rig:asGreen2";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F3A";
	setAttr ".c" -type "float3" 1 1 0 ;
createNode shadingEngine -n "rig:asGreen2SG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F3B";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo14";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F3C";
createNode lambert -n "rig:asBlue";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F3D";
	setAttr ".c" -type "float3" 0 0 1 ;
createNode shadingEngine -n "rig:asBlueSG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F3E";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo15";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F3F";
createNode lambert -n "rig:asBlue2";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F40";
	setAttr ".c" -type "float3" 0 1 1 ;
createNode shadingEngine -n "rig:asBlue2SG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F41";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo16";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F42";
createNode lambert -n "rig:asWhite";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F43";
	setAttr ".c" -type "float3" 1 1 1 ;
createNode shadingEngine -n "rig:asWhiteSG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F44";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo17";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F45";
createNode lambert -n "rig:asBlack";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F46";
	setAttr ".c" -type "float3" 0 0 0 ;
createNode shadingEngine -n "rig:asBlackSG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F47";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo18";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F48";
createNode lambert -n "rig:asBones";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F49";
	setAttr ".c" -type "float3" 0.77999997 0.75999999 0.72000003 ;
createNode shadingEngine -n "rig:asBonesSG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F4A";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo19";
	rename -uid "4A0ED900-0000-438E-5D3D-B42500000F4B";
createNode lambert -n "rig:asFaceBlue";
	rename -uid "4A0ED900-0000-438E-5D3D-B42600000FD9";
	setAttr ".c" -type "float3" 0 0 1 ;
	setAttr ".ambc" -type "float3" 0 0 1 ;
	setAttr ".ic" -type "float3" 0 0 1 ;
createNode shadingEngine -n "rig:asFaceBlueSG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42600000FDA";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo20";
	rename -uid "4A0ED900-0000-438E-5D3D-B42600000FDB";
createNode lambert -n "rig:asFaceBrown";
	rename -uid "4A0ED900-0000-438E-5D3D-B42600000FDC";
	setAttr ".c" -type "float3" 0.54100001 0.28200001 0.2 ;
	setAttr ".ambc" -type "float3" 0.54100001 0.28200001 0.2 ;
	setAttr ".ic" -type "float3" 0.54100001 0.28200001 0.2 ;
createNode shadingEngine -n "rig:asFaceBrownSG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42600000FDD";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo21";
	rename -uid "4A0ED900-0000-438E-5D3D-B42600000FDE";
createNode lambert -n "rig:asFaceGreen";
	rename -uid "4A0ED900-0000-438E-5D3D-B42600000FDF";
	setAttr ".c" -type "float3" 0 0.27500001 0.097999997 ;
	setAttr ".ambc" -type "float3" 0 0.27500001 0.097999997 ;
	setAttr ".ic" -type "float3" 0 0.27500001 0.097999997 ;
createNode shadingEngine -n "rig:asFaceGreenSG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42600000FE0";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo22";
	rename -uid "4A0ED900-0000-438E-5D3D-B42600000FE1";
createNode lambert -n "rig:asFaceCyan";
	rename -uid "4A0ED900-0000-438E-5D3D-B42600000FE2";
	setAttr ".c" -type "float3" 0 0.5 0.5 ;
	setAttr ".ambc" -type "float3" 0 0.5 0.5 ;
	setAttr ".ic" -type "float3" 0 0.5 0.5 ;
createNode shadingEngine -n "rig:asFaceCyanSG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42600000FE3";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo23";
	rename -uid "4A0ED900-0000-438E-5D3D-B42600000FE4";
createNode lambert -n "rig:asFaceRed";
	rename -uid "4A0ED900-0000-438E-5D3D-B42600000FE5";
	setAttr ".c" -type "float3" 0.40000001 0 0 ;
	setAttr ".ambc" -type "float3" 0.40000001 0 0 ;
	setAttr ".ic" -type "float3" 0.40000001 0 0 ;
createNode shadingEngine -n "rig:asFaceRedSG";
	rename -uid "4A0ED900-0000-438E-5D3D-B42600000FE6";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "rig:materialInfo24";
	rename -uid "4A0ED900-0000-438E-5D3D-B42600000FE7";
createNode displayLayer -n "rig:not_working";
	rename -uid "4A0ED900-0000-438E-5D3D-B42600001341";
	setAttr ".v" no;
	setAttr ".do" 2;
select -ne :time1;
	setAttr ".o" 120;
	setAttr ".unw" 120;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
select -ne :renderPartition;
	setAttr -s 25 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 27 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
	setAttr -s 3 ".r";
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :defaultColorMgtGlobals;
	setAttr ".cme" no;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
select -ne :ikSystem;
	setAttr -s 3 ".sol";
connectAttr "persp1_translateX.o" "persp1.tx" -l on;
connectAttr "persp1_translateY.o" "persp1.ty" -l on;
connectAttr "persp1_translateZ.o" "persp1.tz" -l on;
connectAttr "persp1_rotateX.o" "persp1.rx" -l on;
connectAttr "persp1_rotateY.o" "persp1.ry" -l on;
connectAttr "persp1_rotateZ.o" "persp1.rz" -l on;
connectAttr "mmMarkerScale1.ot" "markerGroup1.t";
connectAttr "mmMarkerScale1.os" "markerGroup1.s";
connectAttr "marker1_MKR_translateX.o" "marker1_MKR.tx";
connectAttr "marker1_MKR_translateY.o" "marker1_MKR.ty";
connectAttr "marker1_MKR.deviation" "marker1_MKR.lodv";
connectAttr "bundle1_BND.msg" "marker1_MKR.bundle";
connectAttr "rig:MotionSystem.v" "rig:MainShape.v";
connectAttr "rig:Main.fkVis" "rig:FKSystem.v";
connectAttr "rig:FKSystem_parentConstraint1.ctx" "rig:FKSystem.tx";
connectAttr "rig:FKSystem_parentConstraint1.cty" "rig:FKSystem.ty";
connectAttr "rig:FKSystem_parentConstraint1.ctz" "rig:FKSystem.tz";
connectAttr "rig:FKSystem_parentConstraint1.crx" "rig:FKSystem.rx";
connectAttr "rig:FKSystem_parentConstraint1.cry" "rig:FKSystem.ry";
connectAttr "rig:FKSystem_parentConstraint1.crz" "rig:FKSystem.rz";
connectAttr "rig:FKSystem.ro" "rig:FKSystem_parentConstraint1.cro";
connectAttr "rig:FKSystem.pim" "rig:FKSystem_parentConstraint1.cpim";
connectAttr "rig:FKSystem.rp" "rig:FKSystem_parentConstraint1.crp";
connectAttr "rig:FKSystem.rpt" "rig:FKSystem_parentConstraint1.crt";
connectAttr "rig:RootZeroXform.t" "rig:FKSystem_parentConstraint1.tg[0].tt";
connectAttr "rig:RootZeroXform.rp" "rig:FKSystem_parentConstraint1.tg[0].trp";
connectAttr "rig:RootZeroXform.rpt" "rig:FKSystem_parentConstraint1.tg[0].trt";
connectAttr "rig:RootZeroXform.r" "rig:FKSystem_parentConstraint1.tg[0].tr";
connectAttr "rig:RootZeroXform.ro" "rig:FKSystem_parentConstraint1.tg[0].tro";
connectAttr "rig:RootZeroXform.s" "rig:FKSystem_parentConstraint1.tg[0].ts";
connectAttr "rig:RootZeroXform.pm" "rig:FKSystem_parentConstraint1.tg[0].tpm";
connectAttr "rig:FKSystem_parentConstraint1.w0" "rig:FKSystem_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKParentConstraintToRoot_M_parentConstraint1.ctx" "rig:FKParentConstraintToRoot_M.tx"
		;
connectAttr "rig:FKParentConstraintToRoot_M_parentConstraint1.cty" "rig:FKParentConstraintToRoot_M.ty"
		;
connectAttr "rig:FKParentConstraintToRoot_M_parentConstraint1.ctz" "rig:FKParentConstraintToRoot_M.tz"
		;
connectAttr "rig:FKParentConstraintToRoot_M_parentConstraint1.crx" "rig:FKParentConstraintToRoot_M.rx"
		;
connectAttr "rig:FKParentConstraintToRoot_M_parentConstraint1.cry" "rig:FKParentConstraintToRoot_M.ry"
		;
connectAttr "rig:FKParentConstraintToRoot_M_parentConstraint1.crz" "rig:FKParentConstraintToRoot_M.rz"
		;
connectAttr "rig:FKParentConstraintToRoot_M.ro" "rig:FKParentConstraintToRoot_M_parentConstraint1.cro"
		;
connectAttr "rig:FKParentConstraintToRoot_M.pim" "rig:FKParentConstraintToRoot_M_parentConstraint1.cpim"
		;
connectAttr "rig:FKParentConstraintToRoot_M.rp" "rig:FKParentConstraintToRoot_M_parentConstraint1.crp"
		;
connectAttr "rig:FKParentConstraintToRoot_M.rpt" "rig:FKParentConstraintToRoot_M_parentConstraint1.crt"
		;
connectAttr "rig:LegLockConstrained.t" "rig:FKParentConstraintToRoot_M_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:LegLockConstrained.rp" "rig:FKParentConstraintToRoot_M_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:LegLockConstrained.rpt" "rig:FKParentConstraintToRoot_M_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:LegLockConstrained.r" "rig:FKParentConstraintToRoot_M_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:LegLockConstrained.ro" "rig:FKParentConstraintToRoot_M_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:LegLockConstrained.s" "rig:FKParentConstraintToRoot_M_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:LegLockConstrained.pm" "rig:FKParentConstraintToRoot_M_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKParentConstraintToRoot_M_parentConstraint1.w0" "rig:FKParentConstraintToRoot_M_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:jointLayer.di" "rig:FKOffsetHip_R.do";
connectAttr "rig:FKIKBlendLegCondition_R.ocg" "rig:FKOffsetHip_R.v";
connectAttr "rig:jointLayer.di" "rig:FKXHip_R.do";
connectAttr "rig:FKXHip_R.s" "rig:FKOffsetKnee_R.is";
connectAttr "rig:jointLayer.di" "rig:FKXKnee_R.do";
connectAttr "rig:FKXKnee_R.s" "rig:FKOffsetAnkle_R.is";
connectAttr "rig:jointLayer.di" "rig:FKXAnkle_R.do";
connectAttr "rig:jointLayer.di" "rig:FKOffsetHip_L.do";
connectAttr "rig:FKIKBlendLegCondition_L.ocg" "rig:FKOffsetHip_L.v";
connectAttr "rig:jointLayer.di" "rig:FKXHip_L.do";
connectAttr "rig:FKXHip_L.s" "rig:FKOffsetKnee_L.is";
connectAttr "rig:jointLayer.di" "rig:FKXKnee_L.do";
connectAttr "rig:FKXKnee_L.s" "rig:FKOffsetAnkle_L.is";
connectAttr "rig:jointLayer.di" "rig:FKXAnkle_L.do";
connectAttr "rig:FKParentConstraintToWrist_R_parentConstraint1.ctx" "rig:FKParentConstraintToWrist_R.tx"
		;
connectAttr "rig:FKParentConstraintToWrist_R_parentConstraint1.cty" "rig:FKParentConstraintToWrist_R.ty"
		;
connectAttr "rig:FKParentConstraintToWrist_R_parentConstraint1.ctz" "rig:FKParentConstraintToWrist_R.tz"
		;
connectAttr "rig:FKParentConstraintToWrist_R_parentConstraint1.crx" "rig:FKParentConstraintToWrist_R.rx"
		;
connectAttr "rig:FKParentConstraintToWrist_R_parentConstraint1.cry" "rig:FKParentConstraintToWrist_R.ry"
		;
connectAttr "rig:FKParentConstraintToWrist_R_parentConstraint1.crz" "rig:FKParentConstraintToWrist_R.rz"
		;
connectAttr "rig:Main.fingerVis" "rig:FKParentConstraintToWrist_R.v";
connectAttr "rig:FKParentConstraintToWrist_R_scaleConstraint1.csx" "rig:FKParentConstraintToWrist_R.sx"
		;
connectAttr "rig:FKParentConstraintToWrist_R_scaleConstraint1.csy" "rig:FKParentConstraintToWrist_R.sy"
		;
connectAttr "rig:FKParentConstraintToWrist_R_scaleConstraint1.csz" "rig:FKParentConstraintToWrist_R.sz"
		;
connectAttr "rig:FKParentConstraintToWrist_R.ro" "rig:FKParentConstraintToWrist_R_parentConstraint1.cro"
		;
connectAttr "rig:FKParentConstraintToWrist_R.pim" "rig:FKParentConstraintToWrist_R_parentConstraint1.cpim"
		;
connectAttr "rig:FKParentConstraintToWrist_R.rp" "rig:FKParentConstraintToWrist_R_parentConstraint1.crp"
		;
connectAttr "rig:FKParentConstraintToWrist_R.rpt" "rig:FKParentConstraintToWrist_R_parentConstraint1.crt"
		;
connectAttr "rig:Wrist_R.t" "rig:FKParentConstraintToWrist_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:Wrist_R.rp" "rig:FKParentConstraintToWrist_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:Wrist_R.rpt" "rig:FKParentConstraintToWrist_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:Wrist_R.r" "rig:FKParentConstraintToWrist_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:Wrist_R.ro" "rig:FKParentConstraintToWrist_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:Wrist_R.s" "rig:FKParentConstraintToWrist_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:Wrist_R.pm" "rig:FKParentConstraintToWrist_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:Wrist_R.jo" "rig:FKParentConstraintToWrist_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:FKParentConstraintToWrist_R_parentConstraint1.w0" "rig:FKParentConstraintToWrist_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:jointLayer.di" "rig:FKOffsetIndexFinger1_R.do";
connectAttr "rig:jointLayer.di" "rig:FKXIndexFinger1_R.do";
connectAttr "rig:FKXIndexFinger1_R.s" "rig:FKOffsetIndexFinger2_R.is";
connectAttr "rig:jointLayer.di" "rig:FKXIndexFinger2_R.do";
connectAttr "rig:FKXIndexFinger2_R.s" "rig:FKOffsetIndexFinger3_R.is";
connectAttr "rig:jointLayer.di" "rig:FKXIndexFinger3_R.do";
connectAttr "rig:jointLayer.di" "rig:FKOffsetMiddleFinger1_R.do";
connectAttr "rig:jointLayer.di" "rig:FKXMiddleFinger1_R.do";
connectAttr "rig:FKXMiddleFinger1_R.s" "rig:FKOffsetMiddleFinger2_R.is";
connectAttr "rig:jointLayer.di" "rig:FKXMiddleFinger2_R.do";
connectAttr "rig:FKXMiddleFinger2_R.s" "rig:FKOffsetMiddleFinger3_R.is";
connectAttr "rig:jointLayer.di" "rig:FKXMiddleFinger3_R.do";
connectAttr "rig:jointLayer.di" "rig:FKOffsetCup_R.do";
connectAttr "rig:jointLayer.di" "rig:FKXCup_R.do";
connectAttr "rig:FKXCup_R.s" "rig:FKOffsetPinkyFinger1_R.is";
connectAttr "rig:jointLayer.di" "rig:FKXPinkyFinger1_R.do";
connectAttr "rig:FKXPinkyFinger1_R.s" "rig:FKOffsetPinkyFinger2_R.is";
connectAttr "rig:jointLayer.di" "rig:FKXPinkyFinger2_R.do";
connectAttr "rig:FKXPinkyFinger2_R.s" "rig:FKOffsetPinkyFinger3_R.is";
connectAttr "rig:jointLayer.di" "rig:FKXPinkyFinger3_R.do";
connectAttr "rig:FKXCup_R.s" "rig:FKOffsetRingFinger1_R.is";
connectAttr "rig:jointLayer.di" "rig:FKXRingFinger1_R.do";
connectAttr "rig:FKXRingFinger1_R.s" "rig:FKOffsetRingFinger2_R.is";
connectAttr "rig:jointLayer.di" "rig:FKXRingFinger2_R.do";
connectAttr "rig:FKXRingFinger2_R.s" "rig:FKOffsetRingFinger3_R.is";
connectAttr "rig:jointLayer.di" "rig:FKXRingFinger3_R.do";
connectAttr "rig:jointLayer.di" "rig:FKOffsetThumbFinger1_R.do";
connectAttr "rig:jointLayer.di" "rig:FKXThumbFinger1_R.do";
connectAttr "rig:FKXThumbFinger1_R.s" "rig:FKOffsetThumbFinger2_R.is";
connectAttr "rig:jointLayer.di" "rig:FKXThumbFinger2_R.do";
connectAttr "rig:FKXThumbFinger2_R.s" "rig:FKOffsetThumbFinger3_R.is";
connectAttr "rig:jointLayer.di" "rig:FKXThumbFinger3_R.do";
connectAttr "rig:FKParentConstraintToWrist_R.pim" "rig:FKParentConstraintToWrist_R_scaleConstraint1.cpim"
		;
connectAttr "rig:Wrist_R.s" "rig:FKParentConstraintToWrist_R_scaleConstraint1.tg[0].ts"
		;
connectAttr "rig:Wrist_R.pm" "rig:FKParentConstraintToWrist_R_scaleConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKParentConstraintToWrist_R_scaleConstraint1.w0" "rig:FKParentConstraintToWrist_R_scaleConstraint1.tg[0].tw"
		;
connectAttr "rig:FKParentConstraintToChest_M_parentConstraint1.ctx" "rig:FKParentConstraintToChest_M.tx"
		;
connectAttr "rig:FKParentConstraintToChest_M_parentConstraint1.cty" "rig:FKParentConstraintToChest_M.ty"
		;
connectAttr "rig:FKParentConstraintToChest_M_parentConstraint1.ctz" "rig:FKParentConstraintToChest_M.tz"
		;
connectAttr "rig:FKParentConstraintToChest_M_parentConstraint1.crx" "rig:FKParentConstraintToChest_M.rx"
		;
connectAttr "rig:FKParentConstraintToChest_M_parentConstraint1.cry" "rig:FKParentConstraintToChest_M.ry"
		;
connectAttr "rig:FKParentConstraintToChest_M_parentConstraint1.crz" "rig:FKParentConstraintToChest_M.rz"
		;
connectAttr "rig:FKParentConstraintToChest_M.ro" "rig:FKParentConstraintToChest_M_parentConstraint1.cro"
		;
connectAttr "rig:FKParentConstraintToChest_M.pim" "rig:FKParentConstraintToChest_M_parentConstraint1.cpim"
		;
connectAttr "rig:FKParentConstraintToChest_M.rp" "rig:FKParentConstraintToChest_M_parentConstraint1.crp"
		;
connectAttr "rig:FKParentConstraintToChest_M.rpt" "rig:FKParentConstraintToChest_M_parentConstraint1.crt"
		;
connectAttr "rig:Chest_M.t" "rig:FKParentConstraintToChest_M_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:Chest_M.rp" "rig:FKParentConstraintToChest_M_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:Chest_M.rpt" "rig:FKParentConstraintToChest_M_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:Chest_M.r" "rig:FKParentConstraintToChest_M_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:Chest_M.ro" "rig:FKParentConstraintToChest_M_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:Chest_M.s" "rig:FKParentConstraintToChest_M_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:Chest_M.pm" "rig:FKParentConstraintToChest_M_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:Chest_M.jo" "rig:FKParentConstraintToChest_M_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:FKParentConstraintToChest_M_parentConstraint1.w0" "rig:FKParentConstraintToChest_M_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:jointLayer.di" "rig:FKOffsetScapula_L.do";
connectAttr "rig:jointLayer.di" "rig:FKXScapula_L.do";
connectAttr "rig:FKParentConstraintToSpine2_M_parentConstraint1.ctx" "rig:FKParentConstraintToSpine2_M.tx"
		;
connectAttr "rig:FKParentConstraintToSpine2_M_parentConstraint1.cty" "rig:FKParentConstraintToSpine2_M.ty"
		;
connectAttr "rig:FKParentConstraintToSpine2_M_parentConstraint1.ctz" "rig:FKParentConstraintToSpine2_M.tz"
		;
connectAttr "rig:FKParentConstraintToSpine2_M_parentConstraint1.crx" "rig:FKParentConstraintToSpine2_M.rx"
		;
connectAttr "rig:FKParentConstraintToSpine2_M_parentConstraint1.cry" "rig:FKParentConstraintToSpine2_M.ry"
		;
connectAttr "rig:FKParentConstraintToSpine2_M_parentConstraint1.crz" "rig:FKParentConstraintToSpine2_M.rz"
		;
connectAttr "rig:FKParentConstraintToSpine2_M.ro" "rig:FKParentConstraintToSpine2_M_parentConstraint1.cro"
		;
connectAttr "rig:FKParentConstraintToSpine2_M.pim" "rig:FKParentConstraintToSpine2_M_parentConstraint1.cpim"
		;
connectAttr "rig:FKParentConstraintToSpine2_M.rp" "rig:FKParentConstraintToSpine2_M_parentConstraint1.crp"
		;
connectAttr "rig:FKParentConstraintToSpine2_M.rpt" "rig:FKParentConstraintToSpine2_M_parentConstraint1.crt"
		;
connectAttr "rig:Spine2_M.t" "rig:FKParentConstraintToSpine2_M_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:Spine2_M.rp" "rig:FKParentConstraintToSpine2_M_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:Spine2_M.rpt" "rig:FKParentConstraintToSpine2_M_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:Spine2_M.r" "rig:FKParentConstraintToSpine2_M_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:Spine2_M.ro" "rig:FKParentConstraintToSpine2_M_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:Spine2_M.s" "rig:FKParentConstraintToSpine2_M_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:Spine2_M.pm" "rig:FKParentConstraintToSpine2_M_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:Spine2_M.jo" "rig:FKParentConstraintToSpine2_M_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:FKParentConstraintToSpine2_M_parentConstraint1.w0" "rig:FKParentConstraintToSpine2_M_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:jointLayer.di" "rig:FKOffsetBreast_L.do";
connectAttr "rig:jointLayer.di" "rig:FKXBreast_L.do";
connectAttr "rig:FKIKBlendSpineCondition_M.ocg" "rig:FKOffsetRoot_M.v";
connectAttr "rig:FKOffsetRoot_M_parentConstraint1.ctx" "rig:FKOffsetRoot_M.tx";
connectAttr "rig:FKOffsetRoot_M_parentConstraint1.cty" "rig:FKOffsetRoot_M.ty";
connectAttr "rig:FKOffsetRoot_M_parentConstraint1.ctz" "rig:FKOffsetRoot_M.tz";
connectAttr "rig:FKOffsetRoot_M_parentConstraint1.crx" "rig:FKOffsetRoot_M.rx";
connectAttr "rig:FKOffsetRoot_M_parentConstraint1.cry" "rig:FKOffsetRoot_M.ry";
connectAttr "rig:FKOffsetRoot_M_parentConstraint1.crz" "rig:FKOffsetRoot_M.rz";
connectAttr "rig:jointLayer.di" "rig:FKOffsetRoot_M.do";
connectAttr "rig:jointLayer.di" "rig:FKXRoot_M.do";
connectAttr "rig:FKRoot_M.t" "rig:FKXRoot_M.t";
connectAttr "rig:FKXRoot_M_orientConstraint1.crx" "rig:FKXRoot_M.rx";
connectAttr "rig:FKXRoot_M_orientConstraint1.cry" "rig:FKXRoot_M.ry";
connectAttr "rig:FKXRoot_M_orientConstraint1.crz" "rig:FKXRoot_M.rz";
connectAttr "rig:FKXRoot_M.ro" "rig:FKXRoot_M_orientConstraint1.cro";
connectAttr "rig:FKXRoot_M.pim" "rig:FKXRoot_M_orientConstraint1.cpim";
connectAttr "rig:FKXRoot_M.jo" "rig:FKXRoot_M_orientConstraint1.cjo";
connectAttr "rig:FKRoot_M.r" "rig:FKXRoot_M_orientConstraint1.tg[0].tr";
connectAttr "rig:FKRoot_M.ro" "rig:FKXRoot_M_orientConstraint1.tg[0].tro";
connectAttr "rig:FKRoot_M.pm" "rig:FKXRoot_M_orientConstraint1.tg[0].tpm";
connectAttr "rig:FKXRoot_M_orientConstraint1.w0" "rig:FKXRoot_M_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:FKExtraRoot_M.r" "rig:FKXRoot_M_orientConstraint1.tg[1].tr";
connectAttr "rig:FKExtraRoot_M.ro" "rig:FKXRoot_M_orientConstraint1.tg[1].tro";
connectAttr "rig:FKExtraRoot_M.pm" "rig:FKXRoot_M_orientConstraint1.tg[1].tpm";
connectAttr "rig:FKXRoot_M_orientConstraint1.w1" "rig:FKXRoot_M_orientConstraint1.tg[1].tw"
		;
connectAttr "rig:FKXRoot_M.s" "rig:FKOffsetRootPart1_M.is";
connectAttr "rig:jointLayer.di" "rig:FKXRootPart1_M.do";
connectAttr "rig:FKXRootPart1_M_orientConstraint1.crx" "rig:FKXRootPart1_M.rx";
connectAttr "rig:FKXRootPart1_M_orientConstraint1.cry" "rig:FKXRootPart1_M.ry";
connectAttr "rig:FKXRootPart1_M_orientConstraint1.crz" "rig:FKXRootPart1_M.rz";
connectAttr "rig:FKXRootPart1_M.ro" "rig:FKXRootPart1_M_orientConstraint1.cro";
connectAttr "rig:FKXRootPart1_M.pim" "rig:FKXRootPart1_M_orientConstraint1.cpim"
		;
connectAttr "rig:FKXRootPart1_M.jo" "rig:FKXRootPart1_M_orientConstraint1.cjo";
connectAttr "rig:FKRoot_M.r" "rig:FKXRootPart1_M_orientConstraint1.tg[0].tr";
connectAttr "rig:FKRoot_M.ro" "rig:FKXRootPart1_M_orientConstraint1.tg[0].tro";
connectAttr "rig:FKRoot_M.pm" "rig:FKXRootPart1_M_orientConstraint1.tg[0].tpm";
connectAttr "rig:FKXRootPart1_M_orientConstraint1.w0" "rig:FKXRootPart1_M_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:FKExtraRoot_M.r" "rig:FKXRootPart1_M_orientConstraint1.tg[1].tr"
		;
connectAttr "rig:FKExtraRoot_M.ro" "rig:FKXRootPart1_M_orientConstraint1.tg[1].tro"
		;
connectAttr "rig:FKExtraRoot_M.pm" "rig:FKXRootPart1_M_orientConstraint1.tg[1].tpm"
		;
connectAttr "rig:FKXRootPart1_M_orientConstraint1.w1" "rig:FKXRootPart1_M_orientConstraint1.tg[1].tw"
		;
connectAttr "rig:FKXRootPart1_M.s" "rig:FKOffsetRootPart2_M.is";
connectAttr "rig:jointLayer.di" "rig:FKXRootPart2_M.do";
connectAttr "rig:FKXRootPart2_M_orientConstraint1.crx" "rig:FKXRootPart2_M.rx";
connectAttr "rig:FKXRootPart2_M_orientConstraint1.cry" "rig:FKXRootPart2_M.ry";
connectAttr "rig:FKXRootPart2_M_orientConstraint1.crz" "rig:FKXRootPart2_M.rz";
connectAttr "rig:FKXRootPart2_M.ro" "rig:FKXRootPart2_M_orientConstraint1.cro";
connectAttr "rig:FKXRootPart2_M.pim" "rig:FKXRootPart2_M_orientConstraint1.cpim"
		;
connectAttr "rig:FKXRootPart2_M.jo" "rig:FKXRootPart2_M_orientConstraint1.cjo";
connectAttr "rig:FKRoot_M.r" "rig:FKXRootPart2_M_orientConstraint1.tg[0].tr";
connectAttr "rig:FKRoot_M.ro" "rig:FKXRootPart2_M_orientConstraint1.tg[0].tro";
connectAttr "rig:FKRoot_M.pm" "rig:FKXRootPart2_M_orientConstraint1.tg[0].tpm";
connectAttr "rig:FKXRootPart2_M_orientConstraint1.w0" "rig:FKXRootPart2_M_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:FKExtraRoot_M.r" "rig:FKXRootPart2_M_orientConstraint1.tg[1].tr"
		;
connectAttr "rig:FKExtraRoot_M.ro" "rig:FKXRootPart2_M_orientConstraint1.tg[1].tro"
		;
connectAttr "rig:FKExtraRoot_M.pm" "rig:FKXRootPart2_M_orientConstraint1.tg[1].tpm"
		;
connectAttr "rig:FKXRootPart2_M_orientConstraint1.w1" "rig:FKXRootPart2_M_orientConstraint1.tg[1].tw"
		;
connectAttr "rig:FKXRootPart2_M.s" "rig:FKOffsetSpine1_M.is";
connectAttr "rig:jointLayer.di" "rig:FKXSpine1_M.do";
connectAttr "rig:FKXSpine1_M.s" "rig:FKOffsetSpine2_M.is";
connectAttr "rig:jointLayer.di" "rig:FKXSpine2_M.do";
connectAttr "rig:FKXSpine2_M.s" "rig:FKOffsetChest_M.is";
connectAttr "rig:jointLayer.di" "rig:FKXChest_M.do";
connectAttr "rig:HipSwingerStabilizer_orientConstraint1.crx" "rig:HipSwingerStabilizer.rx"
		;
connectAttr "rig:HipSwingerStabilizer_orientConstraint1.cry" "rig:HipSwingerStabilizer.ry"
		;
connectAttr "rig:HipSwingerStabilizer_orientConstraint1.crz" "rig:HipSwingerStabilizer.rz"
		;
connectAttr "rig:HipSwingerStabilizer.ro" "rig:HipSwingerStabilizer_orientConstraint1.cro"
		;
connectAttr "rig:HipSwingerStabilizer.pim" "rig:HipSwingerStabilizer_orientConstraint1.cpim"
		;
connectAttr "rig:HipSwingerStabilizerTarget.r" "rig:HipSwingerStabilizer_orientConstraint1.tg[0].tr"
		;
connectAttr "rig:HipSwingerStabilizerTarget.ro" "rig:HipSwingerStabilizer_orientConstraint1.tg[0].tro"
		;
connectAttr "rig:HipSwingerStabilizerTarget.pm" "rig:HipSwingerStabilizer_orientConstraint1.tg[0].tpm"
		;
connectAttr "rig:HipSwingerStabilizer_orientConstraint1.w0" "rig:HipSwingerStabilizer_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:HipSwingerStabilizerTarget2.r" "rig:HipSwingerStabilizer_orientConstraint1.tg[1].tr"
		;
connectAttr "rig:HipSwingerStabilizerTarget2.ro" "rig:HipSwingerStabilizer_orientConstraint1.tg[1].tro"
		;
connectAttr "rig:HipSwingerStabilizerTarget2.pm" "rig:HipSwingerStabilizer_orientConstraint1.tg[1].tpm"
		;
connectAttr "rig:HipSwingerStabilizer_orientConstraint1.w1" "rig:HipSwingerStabilizer_orientConstraint1.tg[1].tw"
		;
connectAttr "rig:HipSwingerStabilizerUnitConversion.o" "rig:HipSwingerStabilizer_orientConstraint1.w0"
		;
connectAttr "rig:HipSwingerStabilizerReverse.ox" "rig:HipSwingerStabilizer_orientConstraint1.w1"
		;
connectAttr "rig:FKOffsetRoot_M.ro" "rig:FKOffsetRoot_M_parentConstraint1.cro";
connectAttr "rig:FKOffsetRoot_M.pim" "rig:FKOffsetRoot_M_parentConstraint1.cpim"
		;
connectAttr "rig:FKOffsetRoot_M.rp" "rig:FKOffsetRoot_M_parentConstraint1.crp";
connectAttr "rig:FKOffsetRoot_M.rpt" "rig:FKOffsetRoot_M_parentConstraint1.crt";
connectAttr "rig:FKOffsetRoot_M.jo" "rig:FKOffsetRoot_M_parentConstraint1.cjo";
connectAttr "rig:HipSwingReverseSpine1.t" "rig:FKOffsetRoot_M_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:HipSwingReverseSpine1.rp" "rig:FKOffsetRoot_M_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:HipSwingReverseSpine1.rpt" "rig:FKOffsetRoot_M_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:HipSwingReverseSpine1.r" "rig:FKOffsetRoot_M_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:HipSwingReverseSpine1.ro" "rig:FKOffsetRoot_M_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:HipSwingReverseSpine1.s" "rig:FKOffsetRoot_M_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:HipSwingReverseSpine1.pm" "rig:FKOffsetRoot_M_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKOffsetRoot_M_parentConstraint1.w0" "rig:FKOffsetRoot_M_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKParentConstraintToScapula_L_parentConstraint1.ctx" "rig:FKParentConstraintToScapula_L.tx"
		;
connectAttr "rig:FKParentConstraintToScapula_L_parentConstraint1.cty" "rig:FKParentConstraintToScapula_L.ty"
		;
connectAttr "rig:FKParentConstraintToScapula_L_parentConstraint1.ctz" "rig:FKParentConstraintToScapula_L.tz"
		;
connectAttr "rig:FKParentConstraintToScapula_L_parentConstraint1.crx" "rig:FKParentConstraintToScapula_L.rx"
		;
connectAttr "rig:FKParentConstraintToScapula_L_parentConstraint1.cry" "rig:FKParentConstraintToScapula_L.ry"
		;
connectAttr "rig:FKParentConstraintToScapula_L_parentConstraint1.crz" "rig:FKParentConstraintToScapula_L.rz"
		;
connectAttr "rig:FKParentConstraintToScapula_L.ro" "rig:FKParentConstraintToScapula_L_parentConstraint1.cro"
		;
connectAttr "rig:FKParentConstraintToScapula_L.pim" "rig:FKParentConstraintToScapula_L_parentConstraint1.cpim"
		;
connectAttr "rig:FKParentConstraintToScapula_L.rp" "rig:FKParentConstraintToScapula_L_parentConstraint1.crp"
		;
connectAttr "rig:FKParentConstraintToScapula_L.rpt" "rig:FKParentConstraintToScapula_L_parentConstraint1.crt"
		;
connectAttr "rig:Scapula_L.t" "rig:FKParentConstraintToScapula_L_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:Scapula_L.rp" "rig:FKParentConstraintToScapula_L_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:Scapula_L.rpt" "rig:FKParentConstraintToScapula_L_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:Scapula_L.r" "rig:FKParentConstraintToScapula_L_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:Scapula_L.ro" "rig:FKParentConstraintToScapula_L_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:Scapula_L.s" "rig:FKParentConstraintToScapula_L_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:Scapula_L.pm" "rig:FKParentConstraintToScapula_L_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:Scapula_L.jo" "rig:FKParentConstraintToScapula_L_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:FKParentConstraintToScapula_L_parentConstraint1.w0" "rig:FKParentConstraintToScapula_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:jointLayer.di" "rig:FKOffsetShoulder_L.do";
connectAttr "rig:FKIKBlendArmCondition_L.ocg" "rig:FKOffsetShoulder_L.v";
connectAttr "rig:jointLayer.di" "rig:FKXShoulder_L.do";
connectAttr "rig:FKXShoulder_L.s" "rig:FKOffsetElbow_L.is";
connectAttr "rig:jointLayer.di" "rig:FKXElbow_L.do";
connectAttr "rig:FKXElbow_L.s" "rig:FKOffsetWrist_L.is";
connectAttr "rig:jointLayer.di" "rig:FKXWrist_L.do";
connectAttr "rig:FKIKBlendSpineCondition_M.ocg" "rig:HipSwingerOffset_M.v";
connectAttr "rig:HipSwingReversePart1_orientConstraint1.crx" "rig:HipSwingReversePart1.rx"
		;
connectAttr "rig:HipSwingReversePart1_orientConstraint1.cry" "rig:HipSwingReversePart1.ry"
		;
connectAttr "rig:HipSwingReversePart1_orientConstraint1.crz" "rig:HipSwingReversePart1.rz"
		;
connectAttr "rig:HipSwingReversePart2_orientConstraint1.crx" "rig:HipSwingReversePart2.rx"
		;
connectAttr "rig:HipSwingReversePart2_orientConstraint1.cry" "rig:HipSwingReversePart2.ry"
		;
connectAttr "rig:HipSwingReversePart2_orientConstraint1.crz" "rig:HipSwingReversePart2.rz"
		;
connectAttr "rig:HipSwingReverseSpine1_orientConstraint1.crx" "rig:HipSwingReverseSpine1.rx"
		;
connectAttr "rig:HipSwingReverseSpine1_orientConstraint1.cry" "rig:HipSwingReverseSpine1.ry"
		;
connectAttr "rig:HipSwingReverseSpine1_orientConstraint1.crz" "rig:HipSwingReverseSpine1.rz"
		;
connectAttr "rig:HipSwingReverseSpine1.ro" "rig:HipSwingReverseSpine1_orientConstraint1.cro"
		;
connectAttr "rig:HipSwingReverseSpine1.pim" "rig:HipSwingReverseSpine1_orientConstraint1.cpim"
		;
connectAttr "rig:HipSwinger_M.r" "rig:HipSwingReverseSpine1_orientConstraint1.tg[0].tr"
		;
connectAttr "rig:HipSwinger_M.ro" "rig:HipSwingReverseSpine1_orientConstraint1.tg[0].tro"
		;
connectAttr "rig:HipSwinger_M.pm" "rig:HipSwingReverseSpine1_orientConstraint1.tg[0].tpm"
		;
connectAttr "rig:HipSwingReverseSpine1_orientConstraint1.w0" "rig:HipSwingReverseSpine1_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:HipSwingReversePart2.ro" "rig:HipSwingReversePart2_orientConstraint1.cro"
		;
connectAttr "rig:HipSwingReversePart2.pim" "rig:HipSwingReversePart2_orientConstraint1.cpim"
		;
connectAttr "rig:HipSwingerStabilizerTarget.r" "rig:HipSwingReversePart2_orientConstraint1.tg[0].tr"
		;
connectAttr "rig:HipSwingerStabilizerTarget.ro" "rig:HipSwingReversePart2_orientConstraint1.tg[0].tro"
		;
connectAttr "rig:HipSwingerStabilizerTarget.pm" "rig:HipSwingReversePart2_orientConstraint1.tg[0].tpm"
		;
connectAttr "rig:HipSwingReversePart2_orientConstraint1.w0" "rig:HipSwingReversePart2_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:HipSwinger_M.r" "rig:HipSwingReversePart2_orientConstraint1.tg[1].tr"
		;
connectAttr "rig:HipSwinger_M.ro" "rig:HipSwingReversePart2_orientConstraint1.tg[1].tro"
		;
connectAttr "rig:HipSwinger_M.pm" "rig:HipSwingReversePart2_orientConstraint1.tg[1].tpm"
		;
connectAttr "rig:HipSwingReversePart2_orientConstraint1.w1" "rig:HipSwingReversePart2_orientConstraint1.tg[1].tw"
		;
connectAttr "rig:HipSwingReversePart1.ro" "rig:HipSwingReversePart1_orientConstraint1.cro"
		;
connectAttr "rig:HipSwingReversePart1.pim" "rig:HipSwingReversePart1_orientConstraint1.cpim"
		;
connectAttr "rig:HipSwingerStabilizerTarget.r" "rig:HipSwingReversePart1_orientConstraint1.tg[0].tr"
		;
connectAttr "rig:HipSwingerStabilizerTarget.ro" "rig:HipSwingReversePart1_orientConstraint1.tg[0].tro"
		;
connectAttr "rig:HipSwingerStabilizerTarget.pm" "rig:HipSwingReversePart1_orientConstraint1.tg[0].tpm"
		;
connectAttr "rig:HipSwingReversePart1_orientConstraint1.w0" "rig:HipSwingReversePart1_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:HipSwinger_M.r" "rig:HipSwingReversePart1_orientConstraint1.tg[1].tr"
		;
connectAttr "rig:HipSwinger_M.ro" "rig:HipSwingReversePart1_orientConstraint1.tg[1].tro"
		;
connectAttr "rig:HipSwinger_M.pm" "rig:HipSwingReversePart1_orientConstraint1.tg[1].tpm"
		;
connectAttr "rig:HipSwingReversePart1_orientConstraint1.w1" "rig:HipSwingReversePart1_orientConstraint1.tg[1].tw"
		;
connectAttr "rig:Main.fkIkVis" "rig:FKIKSystem.v";
connectAttr "rig:FKIKParentConstraintSpine_M_parentConstraint1.ctx" "rig:FKIKParentConstraintSpine_M.tx"
		;
connectAttr "rig:FKIKParentConstraintSpine_M_parentConstraint1.cty" "rig:FKIKParentConstraintSpine_M.ty"
		;
connectAttr "rig:FKIKParentConstraintSpine_M_parentConstraint1.ctz" "rig:FKIKParentConstraintSpine_M.tz"
		;
connectAttr "rig:FKIKParentConstraintSpine_M_parentConstraint1.crx" "rig:FKIKParentConstraintSpine_M.rx"
		;
connectAttr "rig:FKIKParentConstraintSpine_M_parentConstraint1.cry" "rig:FKIKParentConstraintSpine_M.ry"
		;
connectAttr "rig:FKIKParentConstraintSpine_M_parentConstraint1.crz" "rig:FKIKParentConstraintSpine_M.rz"
		;
connectAttr "rig:FKIKParentConstraintSpine_M.ro" "rig:FKIKParentConstraintSpine_M_parentConstraint1.cro"
		;
connectAttr "rig:FKIKParentConstraintSpine_M.pim" "rig:FKIKParentConstraintSpine_M_parentConstraint1.cpim"
		;
connectAttr "rig:FKIKParentConstraintSpine_M.rp" "rig:FKIKParentConstraintSpine_M_parentConstraint1.crp"
		;
connectAttr "rig:FKIKParentConstraintSpine_M.rpt" "rig:FKIKParentConstraintSpine_M_parentConstraint1.crt"
		;
connectAttr "rig:Root_M.t" "rig:FKIKParentConstraintSpine_M_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:Root_M.rp" "rig:FKIKParentConstraintSpine_M_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:Root_M.rpt" "rig:FKIKParentConstraintSpine_M_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:Root_M.r" "rig:FKIKParentConstraintSpine_M_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:Root_M.ro" "rig:FKIKParentConstraintSpine_M_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:Root_M.s" "rig:FKIKParentConstraintSpine_M_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:Root_M.pm" "rig:FKIKParentConstraintSpine_M_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:Root_M.jo" "rig:FKIKParentConstraintSpine_M_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:FKIKParentConstraintSpine_M_parentConstraint1.w0" "rig:FKIKParentConstraintSpine_M_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKParentConstraintArm_L_parentConstraint1.ctx" "rig:FKIKParentConstraintArm_L.tx"
		;
connectAttr "rig:FKIKParentConstraintArm_L_parentConstraint1.cty" "rig:FKIKParentConstraintArm_L.ty"
		;
connectAttr "rig:FKIKParentConstraintArm_L_parentConstraint1.ctz" "rig:FKIKParentConstraintArm_L.tz"
		;
connectAttr "rig:FKIKParentConstraintArm_L_parentConstraint1.crx" "rig:FKIKParentConstraintArm_L.rx"
		;
connectAttr "rig:FKIKParentConstraintArm_L_parentConstraint1.cry" "rig:FKIKParentConstraintArm_L.ry"
		;
connectAttr "rig:FKIKParentConstraintArm_L_parentConstraint1.crz" "rig:FKIKParentConstraintArm_L.rz"
		;
connectAttr "rig:FKIKParentConstraintArm_L.ro" "rig:FKIKParentConstraintArm_L_parentConstraint1.cro"
		;
connectAttr "rig:FKIKParentConstraintArm_L.pim" "rig:FKIKParentConstraintArm_L_parentConstraint1.cpim"
		;
connectAttr "rig:FKIKParentConstraintArm_L.rp" "rig:FKIKParentConstraintArm_L_parentConstraint1.crp"
		;
connectAttr "rig:FKIKParentConstraintArm_L.rpt" "rig:FKIKParentConstraintArm_L_parentConstraint1.crt"
		;
connectAttr "rig:Scapula_L.t" "rig:FKIKParentConstraintArm_L_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:Scapula_L.rp" "rig:FKIKParentConstraintArm_L_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:Scapula_L.rpt" "rig:FKIKParentConstraintArm_L_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:Scapula_L.r" "rig:FKIKParentConstraintArm_L_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:Scapula_L.ro" "rig:FKIKParentConstraintArm_L_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:Scapula_L.s" "rig:FKIKParentConstraintArm_L_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:Scapula_L.pm" "rig:FKIKParentConstraintArm_L_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:Scapula_L.jo" "rig:FKIKParentConstraintArm_L_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:FKIKParentConstraintArm_L_parentConstraint1.w0" "rig:FKIKParentConstraintArm_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:LegLockConstrained_pointConstraint1.ctx" "rig:LegLockConstrained.tx"
		;
connectAttr "rig:LegLockConstrained_pointConstraint1.cty" "rig:LegLockConstrained.ty"
		;
connectAttr "rig:LegLockConstrained_pointConstraint1.ctz" "rig:LegLockConstrained.tz"
		;
connectAttr "rig:LegLockConstrained_orientConstraint1.crx" "rig:LegLockConstrained.rx"
		;
connectAttr "rig:LegLockConstrained_orientConstraint1.cry" "rig:LegLockConstrained.ry"
		;
connectAttr "rig:LegLockConstrained_orientConstraint1.crz" "rig:LegLockConstrained.rz"
		;
connectAttr "rig:LegLockConstrained.pim" "rig:LegLockConstrained_pointConstraint1.cpim"
		;
connectAttr "rig:LegLockConstrained.rp" "rig:LegLockConstrained_pointConstraint1.crp"
		;
connectAttr "rig:LegLockConstrained.rpt" "rig:LegLockConstrained_pointConstraint1.crt"
		;
connectAttr "rig:Root_M.t" "rig:LegLockConstrained_pointConstraint1.tg[0].tt";
connectAttr "rig:Root_M.rp" "rig:LegLockConstrained_pointConstraint1.tg[0].trp";
connectAttr "rig:Root_M.rpt" "rig:LegLockConstrained_pointConstraint1.tg[0].trt"
		;
connectAttr "rig:Root_M.pm" "rig:LegLockConstrained_pointConstraint1.tg[0].tpm";
connectAttr "rig:LegLockConstrained_pointConstraint1.w0" "rig:LegLockConstrained_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:LegLockConstrained.ro" "rig:LegLockConstrained_orientConstraint1.cro"
		;
connectAttr "rig:LegLockConstrained.pim" "rig:LegLockConstrained_orientConstraint1.cpim"
		;
connectAttr "rig:RootX_M.r" "rig:LegLockConstrained_orientConstraint1.tg[0].tr";
connectAttr "rig:RootX_M.ro" "rig:LegLockConstrained_orientConstraint1.tg[0].tro"
		;
connectAttr "rig:RootX_M.pm" "rig:LegLockConstrained_orientConstraint1.tg[0].tpm"
		;
connectAttr "rig:LegLockConstrained_orientConstraint1.w0" "rig:LegLockConstrained_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:RootSpineAligned.r" "rig:LegLockConstrained_orientConstraint1.tg[1].tr"
		;
connectAttr "rig:RootSpineAligned.ro" "rig:LegLockConstrained_orientConstraint1.tg[1].tro"
		;
connectAttr "rig:RootSpineAligned.pm" "rig:LegLockConstrained_orientConstraint1.tg[1].tpm"
		;
connectAttr "rig:LegLockConstrained_orientConstraint1.w1" "rig:LegLockConstrained_orientConstraint1.tg[1].tw"
		;
connectAttr "rig:LegLockUnitConversion.o" "rig:LegLockConstrained_orientConstraint1.w0"
		;
connectAttr "rig:LegLockReverse.ox" "rig:LegLockConstrained_orientConstraint1.w1"
		;
connectAttr "rig:RootCenterBtwLegsBlended_M_parentConstraint1.ctx" "rig:RootCenterBtwLegsBlended_M.tx"
		;
connectAttr "rig:RootCenterBtwLegsBlended_M_parentConstraint1.cty" "rig:RootCenterBtwLegsBlended_M.ty"
		;
connectAttr "rig:RootCenterBtwLegsBlended_M_parentConstraint1.ctz" "rig:RootCenterBtwLegsBlended_M.tz"
		;
connectAttr "rig:RootCenterBtwLegsBlended_M_parentConstraint1.crx" "rig:RootCenterBtwLegsBlended_M.rx"
		;
connectAttr "rig:RootCenterBtwLegsBlended_M_parentConstraint1.cry" "rig:RootCenterBtwLegsBlended_M.ry"
		;
connectAttr "rig:RootCenterBtwLegsBlended_M_parentConstraint1.crz" "rig:RootCenterBtwLegsBlended_M.rz"
		;
connectAttr "rig:RootSpineAligned_orientConstraint1.crx" "rig:RootSpineAligned.rx"
		;
connectAttr "rig:RootSpineAligned_orientConstraint1.cry" "rig:RootSpineAligned.ry"
		;
connectAttr "rig:RootSpineAligned_orientConstraint1.crz" "rig:RootSpineAligned.rz"
		;
connectAttr "rig:RootSpineAligned.ro" "rig:RootSpineAligned_orientConstraint1.cro"
		;
connectAttr "rig:RootSpineAligned.pim" "rig:RootSpineAligned_orientConstraint1.cpim"
		;
connectAttr "rig:Root_M.r" "rig:RootSpineAligned_orientConstraint1.tg[0].tr";
connectAttr "rig:Root_M.ro" "rig:RootSpineAligned_orientConstraint1.tg[0].tro";
connectAttr "rig:Root_M.pm" "rig:RootSpineAligned_orientConstraint1.tg[0].tpm";
connectAttr "rig:Root_M.jo" "rig:RootSpineAligned_orientConstraint1.tg[0].tjo";
connectAttr "rig:RootSpineAligned_orientConstraint1.w0" "rig:RootSpineAligned_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:RootCenterBtwLegsBlended_M.ro" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.cro"
		;
connectAttr "rig:RootCenterBtwLegsBlended_M.pim" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.cpim"
		;
connectAttr "rig:RootCenterBtwLegsBlended_M.rp" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.crp"
		;
connectAttr "rig:RootCenterBtwLegsBlended_M.rpt" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.crt"
		;
connectAttr "rig:RootCenter_M.t" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:RootCenter_M.rp" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:RootCenter_M.rpt" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:RootCenter_M.r" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:RootCenter_M.ro" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:RootCenter_M.s" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:RootCenter_M.pm" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:RootCenterBtwLegsBlended_M_parentConstraint1.w0" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:RootCenterBtwLegsOffset_M.t" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.tg[1].tt"
		;
connectAttr "rig:RootCenterBtwLegsOffset_M.rp" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.tg[1].trp"
		;
connectAttr "rig:RootCenterBtwLegsOffset_M.rpt" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.tg[1].trt"
		;
connectAttr "rig:RootCenterBtwLegsOffset_M.r" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.tg[1].tr"
		;
connectAttr "rig:RootCenterBtwLegsOffset_M.ro" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.tg[1].tro"
		;
connectAttr "rig:RootCenterBtwLegsOffset_M.s" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.tg[1].ts"
		;
connectAttr "rig:RootCenterBtwLegsOffset_M.pm" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.tg[1].tpm"
		;
connectAttr "rig:RootCenterBtwLegsBlended_M_parentConstraint1.w1" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.tg[1].tw"
		;
connectAttr "rig:CenterBtwLegsUnitReverse.ox" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.w0"
		;
connectAttr "rig:CenterBtwLegsUnitConversion.o" "rig:RootCenterBtwLegsBlended_M_parentConstraint1.w1"
		;
connectAttr "rig:UnTwistNeck1_M.msg" "rig:UnTwistIKNeck1_M.hsj";
connectAttr "rig:effector1.hp" "rig:UnTwistIKNeck1_M.hee";
connectAttr "rig:ikRPsolver.msg" "rig:UnTwistIKNeck1_M.hsv";
connectAttr "rig:UnTwistIKNeck1_M_poleVectorConstraint1.ctx" "rig:UnTwistIKNeck1_M.pvx"
		;
connectAttr "rig:UnTwistIKNeck1_M_poleVectorConstraint1.cty" "rig:UnTwistIKNeck1_M.pvy"
		;
connectAttr "rig:UnTwistIKNeck1_M_poleVectorConstraint1.ctz" "rig:UnTwistIKNeck1_M.pvz"
		;
connectAttr "rig:UnTwistIKNeck1_M.pim" "rig:UnTwistIKNeck1_M_poleVectorConstraint1.cpim"
		;
connectAttr "rig:UnTwistNeck1_M.pm" "rig:UnTwistIKNeck1_M_poleVectorConstraint1.ps"
		;
connectAttr "rig:UnTwistNeck1_M.t" "rig:UnTwistIKNeck1_M_poleVectorConstraint1.crp"
		;
connectAttr "rig:UnTwistNeck1_M.t" "rig:UnTwistIKNeck1_M_poleVectorConstraint1.tg[0].tt"
		;
connectAttr "rig:UnTwistNeck1_M.rp" "rig:UnTwistIKNeck1_M_poleVectorConstraint1.tg[0].trp"
		;
connectAttr "rig:UnTwistNeck1_M.rpt" "rig:UnTwistIKNeck1_M_poleVectorConstraint1.tg[0].trt"
		;
connectAttr "rig:UnTwistNeck1_M.pm" "rig:UnTwistIKNeck1_M_poleVectorConstraint1.tg[0].tpm"
		;
connectAttr "rig:UnTwistIKNeck1_M_poleVectorConstraint1.w0" "rig:UnTwistIKNeck1_M_poleVectorConstraint1.tg[0].tw"
		;
connectAttr "rig:UnTwistNeck1_M.s" "rig:UnTwistEndNeck1_M.is";
connectAttr "rig:UnTwistEndNeck1_M.tx" "rig:effector1.tx";
connectAttr "rig:UnTwistEndNeck1_M.ty" "rig:effector1.ty";
connectAttr "rig:UnTwistEndNeck1_M.tz" "rig:effector1.tz";
connectAttr "rig:UnTwistNeck1_M.s" "rig:TwistBalancerNeck1_M.is";
connectAttr "rig:UnTwistChest_M.msg" "rig:UnTwistIKChest_M.hsj";
connectAttr "rig:effector2.hp" "rig:UnTwistIKChest_M.hee";
connectAttr "rig:ikRPsolver.msg" "rig:UnTwistIKChest_M.hsv";
connectAttr "rig:UnTwistIKChest_M_poleVectorConstraint1.ctx" "rig:UnTwistIKChest_M.pvx"
		;
connectAttr "rig:UnTwistIKChest_M_poleVectorConstraint1.cty" "rig:UnTwistIKChest_M.pvy"
		;
connectAttr "rig:UnTwistIKChest_M_poleVectorConstraint1.ctz" "rig:UnTwistIKChest_M.pvz"
		;
connectAttr "rig:UnTwistIKChest_M.pim" "rig:UnTwistIKChest_M_poleVectorConstraint1.cpim"
		;
connectAttr "rig:UnTwistChest_M.pm" "rig:UnTwistIKChest_M_poleVectorConstraint1.ps"
		;
connectAttr "rig:UnTwistChest_M.t" "rig:UnTwistIKChest_M_poleVectorConstraint1.crp"
		;
connectAttr "rig:UnTwistChest_M.t" "rig:UnTwistIKChest_M_poleVectorConstraint1.tg[0].tt"
		;
connectAttr "rig:UnTwistChest_M.rp" "rig:UnTwistIKChest_M_poleVectorConstraint1.tg[0].trp"
		;
connectAttr "rig:UnTwistChest_M.rpt" "rig:UnTwistIKChest_M_poleVectorConstraint1.tg[0].trt"
		;
connectAttr "rig:UnTwistChest_M.pm" "rig:UnTwistIKChest_M_poleVectorConstraint1.tg[0].tpm"
		;
connectAttr "rig:UnTwistIKChest_M_poleVectorConstraint1.w0" "rig:UnTwistIKChest_M_poleVectorConstraint1.tg[0].tw"
		;
connectAttr "rig:UnTwistChest_M.s" "rig:UnTwistEndChest_M.is";
connectAttr "rig:UnTwistEndChest_M.tx" "rig:effector2.tx";
connectAttr "rig:UnTwistEndChest_M.ty" "rig:effector2.ty";
connectAttr "rig:UnTwistEndChest_M.tz" "rig:effector2.tz";
connectAttr "rig:UnTwistChest_M.s" "rig:TwistBalancerChest_M.is";
connectAttr "rig:TwistFollowKnee_R_parentConstraint1.ctx" "rig:TwistFollowKnee_R.tx"
		;
connectAttr "rig:TwistFollowKnee_R_parentConstraint1.cty" "rig:TwistFollowKnee_R.ty"
		;
connectAttr "rig:TwistFollowKnee_R_parentConstraint1.ctz" "rig:TwistFollowKnee_R.tz"
		;
connectAttr "rig:TwistFollowKnee_R_parentConstraint1.crx" "rig:TwistFollowKnee_R.rx"
		;
connectAttr "rig:TwistFollowKnee_R_parentConstraint1.cry" "rig:TwistFollowKnee_R.ry"
		;
connectAttr "rig:TwistFollowKnee_R_parentConstraint1.crz" "rig:TwistFollowKnee_R.rz"
		;
connectAttr "rig:TwistFollowKnee_R.ro" "rig:TwistFollowKnee_R_parentConstraint1.cro"
		;
connectAttr "rig:TwistFollowKnee_R.pim" "rig:TwistFollowKnee_R_parentConstraint1.cpim"
		;
connectAttr "rig:TwistFollowKnee_R.rp" "rig:TwistFollowKnee_R_parentConstraint1.crp"
		;
connectAttr "rig:TwistFollowKnee_R.rpt" "rig:TwistFollowKnee_R_parentConstraint1.crt"
		;
connectAttr "rig:FKXKnee_R.t" "rig:TwistFollowKnee_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXKnee_R.rp" "rig:TwistFollowKnee_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXKnee_R.rpt" "rig:TwistFollowKnee_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXKnee_R.r" "rig:TwistFollowKnee_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXKnee_R.ro" "rig:TwistFollowKnee_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXKnee_R.s" "rig:TwistFollowKnee_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXKnee_R.pm" "rig:TwistFollowKnee_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXKnee_R.jo" "rig:TwistFollowKnee_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistFollowKnee_R_parentConstraint1.w0" "rig:TwistFollowKnee_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:UnTwistKnee_R.msg" "rig:UnTwistIKKnee_R.hsj";
connectAttr "rig:effector3.hp" "rig:UnTwistIKKnee_R.hee";
connectAttr "rig:ikRPsolver.msg" "rig:UnTwistIKKnee_R.hsv";
connectAttr "rig:UnTwistIKKnee_R_poleVectorConstraint1.ctx" "rig:UnTwistIKKnee_R.pvx"
		;
connectAttr "rig:UnTwistIKKnee_R_poleVectorConstraint1.cty" "rig:UnTwistIKKnee_R.pvy"
		;
connectAttr "rig:UnTwistIKKnee_R_poleVectorConstraint1.ctz" "rig:UnTwistIKKnee_R.pvz"
		;
connectAttr "rig:UnTwistIKKnee_R.pim" "rig:UnTwistIKKnee_R_poleVectorConstraint1.cpim"
		;
connectAttr "rig:UnTwistKnee_R.pm" "rig:UnTwistIKKnee_R_poleVectorConstraint1.ps"
		;
connectAttr "rig:UnTwistKnee_R.t" "rig:UnTwistIKKnee_R_poleVectorConstraint1.crp"
		;
connectAttr "rig:UnTwistKnee_R.t" "rig:UnTwistIKKnee_R_poleVectorConstraint1.tg[0].tt"
		;
connectAttr "rig:UnTwistKnee_R.rp" "rig:UnTwistIKKnee_R_poleVectorConstraint1.tg[0].trp"
		;
connectAttr "rig:UnTwistKnee_R.rpt" "rig:UnTwistIKKnee_R_poleVectorConstraint1.tg[0].trt"
		;
connectAttr "rig:UnTwistKnee_R.pm" "rig:UnTwistIKKnee_R_poleVectorConstraint1.tg[0].tpm"
		;
connectAttr "rig:UnTwistIKKnee_R_poleVectorConstraint1.w0" "rig:UnTwistIKKnee_R_poleVectorConstraint1.tg[0].tw"
		;
connectAttr "rig:TwistFollowParentKnee_R_parentConstraint1.ctx" "rig:TwistFollowParentKnee_R.tx"
		;
connectAttr "rig:TwistFollowParentKnee_R_parentConstraint1.cty" "rig:TwistFollowParentKnee_R.ty"
		;
connectAttr "rig:TwistFollowParentKnee_R_parentConstraint1.ctz" "rig:TwistFollowParentKnee_R.tz"
		;
connectAttr "rig:TwistFollowParentKnee_R_parentConstraint1.crx" "rig:TwistFollowParentKnee_R.rx"
		;
connectAttr "rig:TwistFollowParentKnee_R_parentConstraint1.cry" "rig:TwistFollowParentKnee_R.ry"
		;
connectAttr "rig:TwistFollowParentKnee_R_parentConstraint1.crz" "rig:TwistFollowParentKnee_R.rz"
		;
connectAttr "rig:TwistFollowParentKnee_R.ro" "rig:TwistFollowParentKnee_R_parentConstraint1.cro"
		;
connectAttr "rig:TwistFollowParentKnee_R.pim" "rig:TwistFollowParentKnee_R_parentConstraint1.cpim"
		;
connectAttr "rig:TwistFollowParentKnee_R.rp" "rig:TwistFollowParentKnee_R_parentConstraint1.crp"
		;
connectAttr "rig:TwistFollowParentKnee_R.rpt" "rig:TwistFollowParentKnee_R_parentConstraint1.crt"
		;
connectAttr "rig:FKXHip_R.t" "rig:TwistFollowParentKnee_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXHip_R.rp" "rig:TwistFollowParentKnee_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXHip_R.rpt" "rig:TwistFollowParentKnee_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXHip_R.r" "rig:TwistFollowParentKnee_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXHip_R.ro" "rig:TwistFollowParentKnee_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXHip_R.s" "rig:TwistFollowParentKnee_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXHip_R.pm" "rig:TwistFollowParentKnee_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXHip_R.jo" "rig:TwistFollowParentKnee_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistFollowParentKnee_R_parentConstraint1.w0" "rig:TwistFollowParentKnee_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:UnTwistKnee_R_pointConstraint1.ctx" "rig:UnTwistKnee_R.tx";
connectAttr "rig:UnTwistKnee_R_pointConstraint1.cty" "rig:UnTwistKnee_R.ty";
connectAttr "rig:UnTwistKnee_R_pointConstraint1.ctz" "rig:UnTwistKnee_R.tz";
connectAttr "rig:UnTwistKnee_R.s" "rig:UnTwistEndKnee_R.is";
connectAttr "rig:UnTwistKnee_R.pim" "rig:UnTwistKnee_R_pointConstraint1.cpim";
connectAttr "rig:UnTwistKnee_R.rp" "rig:UnTwistKnee_R_pointConstraint1.crp";
connectAttr "rig:UnTwistKnee_R.rpt" "rig:UnTwistKnee_R_pointConstraint1.crt";
connectAttr "rig:FKXKnee_R.t" "rig:UnTwistKnee_R_pointConstraint1.tg[0].tt";
connectAttr "rig:FKXKnee_R.rp" "rig:UnTwistKnee_R_pointConstraint1.tg[0].trp";
connectAttr "rig:FKXKnee_R.rpt" "rig:UnTwistKnee_R_pointConstraint1.tg[0].trt";
connectAttr "rig:FKXKnee_R.pm" "rig:UnTwistKnee_R_pointConstraint1.tg[0].tpm";
connectAttr "rig:UnTwistKnee_R_pointConstraint1.w0" "rig:UnTwistKnee_R_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:UnTwistEndKnee_R.tx" "rig:effector3.tx";
connectAttr "rig:UnTwistEndKnee_R.ty" "rig:effector3.ty";
connectAttr "rig:UnTwistEndKnee_R.tz" "rig:effector3.tz";
connectAttr "rig:UnTwistKnee_R.s" "rig:TwistBalancerKnee_R.is";
connectAttr "rig:TwistBalancerKnee_R_parentConstraint1.ctx" "rig:TwistBalancerKnee_R.tx"
		;
connectAttr "rig:TwistBalancerKnee_R_parentConstraint1.cty" "rig:TwistBalancerKnee_R.ty"
		;
connectAttr "rig:TwistBalancerKnee_R_parentConstraint1.ctz" "rig:TwistBalancerKnee_R.tz"
		;
connectAttr "rig:TwistBalancerKnee_R_parentConstraint1.crx" "rig:TwistBalancerKnee_R.rx"
		;
connectAttr "rig:TwistBalancerKnee_R_parentConstraint1.cry" "rig:TwistBalancerKnee_R.ry"
		;
connectAttr "rig:TwistBalancerKnee_R_parentConstraint1.crz" "rig:TwistBalancerKnee_R.rz"
		;
connectAttr "rig:TwistBalancerKnee_R.ro" "rig:TwistBalancerKnee_R_parentConstraint1.cro"
		;
connectAttr "rig:TwistBalancerKnee_R.pim" "rig:TwistBalancerKnee_R_parentConstraint1.cpim"
		;
connectAttr "rig:TwistBalancerKnee_R.rp" "rig:TwistBalancerKnee_R_parentConstraint1.crp"
		;
connectAttr "rig:TwistBalancerKnee_R.rpt" "rig:TwistBalancerKnee_R_parentConstraint1.crt"
		;
connectAttr "rig:TwistBalancerKnee_R.jo" "rig:TwistBalancerKnee_R_parentConstraint1.cjo"
		;
connectAttr "rig:FKXKnee_R.t" "rig:TwistBalancerKnee_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXKnee_R.rp" "rig:TwistBalancerKnee_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXKnee_R.rpt" "rig:TwistBalancerKnee_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXKnee_R.r" "rig:TwistBalancerKnee_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXKnee_R.ro" "rig:TwistBalancerKnee_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXKnee_R.s" "rig:TwistBalancerKnee_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXKnee_R.pm" "rig:TwistBalancerKnee_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXKnee_R.jo" "rig:TwistBalancerKnee_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistBalancerKnee_R_parentConstraint1.w0" "rig:TwistBalancerKnee_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:unitConversion31.o" "rig:TwisterKnee0_R.rx";
connectAttr "rig:unitConversion33.o" "rig:TwisterKnee1_R.rx";
connectAttr "rig:unitConversion35.o" "rig:TwisterKnee2_R.rx";
connectAttr "rig:TwistFollowHip_R_parentConstraint1.ctx" "rig:TwistFollowHip_R.tx"
		;
connectAttr "rig:TwistFollowHip_R_parentConstraint1.cty" "rig:TwistFollowHip_R.ty"
		;
connectAttr "rig:TwistFollowHip_R_parentConstraint1.ctz" "rig:TwistFollowHip_R.tz"
		;
connectAttr "rig:TwistFollowHip_R_parentConstraint1.crx" "rig:TwistFollowHip_R.rx"
		;
connectAttr "rig:TwistFollowHip_R_parentConstraint1.cry" "rig:TwistFollowHip_R.ry"
		;
connectAttr "rig:TwistFollowHip_R_parentConstraint1.crz" "rig:TwistFollowHip_R.rz"
		;
connectAttr "rig:TwistFollowHip_R.ro" "rig:TwistFollowHip_R_parentConstraint1.cro"
		;
connectAttr "rig:TwistFollowHip_R.pim" "rig:TwistFollowHip_R_parentConstraint1.cpim"
		;
connectAttr "rig:TwistFollowHip_R.rp" "rig:TwistFollowHip_R_parentConstraint1.crp"
		;
connectAttr "rig:TwistFollowHip_R.rpt" "rig:TwistFollowHip_R_parentConstraint1.crt"
		;
connectAttr "rig:FKXHip_R.t" "rig:TwistFollowHip_R_parentConstraint1.tg[0].tt";
connectAttr "rig:FKXHip_R.rp" "rig:TwistFollowHip_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXHip_R.rpt" "rig:TwistFollowHip_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXHip_R.r" "rig:TwistFollowHip_R_parentConstraint1.tg[0].tr";
connectAttr "rig:FKXHip_R.ro" "rig:TwistFollowHip_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXHip_R.s" "rig:TwistFollowHip_R_parentConstraint1.tg[0].ts";
connectAttr "rig:FKXHip_R.pm" "rig:TwistFollowHip_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXHip_R.jo" "rig:TwistFollowHip_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistFollowHip_R_parentConstraint1.w0" "rig:TwistFollowHip_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:UnTwistHip_R.msg" "rig:UnTwistIKHip_R.hsj";
connectAttr "rig:effector4.hp" "rig:UnTwistIKHip_R.hee";
connectAttr "rig:ikRPsolver.msg" "rig:UnTwistIKHip_R.hsv";
connectAttr "rig:UnTwistIKHip_R_poleVectorConstraint1.ctx" "rig:UnTwistIKHip_R.pvx"
		;
connectAttr "rig:UnTwistIKHip_R_poleVectorConstraint1.cty" "rig:UnTwistIKHip_R.pvy"
		;
connectAttr "rig:UnTwistIKHip_R_poleVectorConstraint1.ctz" "rig:UnTwistIKHip_R.pvz"
		;
connectAttr "rig:UnTwistIKHip_R.pim" "rig:UnTwistIKHip_R_poleVectorConstraint1.cpim"
		;
connectAttr "rig:UnTwistHip_R.pm" "rig:UnTwistIKHip_R_poleVectorConstraint1.ps";
connectAttr "rig:UnTwistHip_R.t" "rig:UnTwistIKHip_R_poleVectorConstraint1.crp";
connectAttr "rig:UnTwistHip_R.t" "rig:UnTwistIKHip_R_poleVectorConstraint1.tg[0].tt"
		;
connectAttr "rig:UnTwistHip_R.rp" "rig:UnTwistIKHip_R_poleVectorConstraint1.tg[0].trp"
		;
connectAttr "rig:UnTwistHip_R.rpt" "rig:UnTwistIKHip_R_poleVectorConstraint1.tg[0].trt"
		;
connectAttr "rig:UnTwistHip_R.pm" "rig:UnTwistIKHip_R_poleVectorConstraint1.tg[0].tpm"
		;
connectAttr "rig:UnTwistIKHip_R_poleVectorConstraint1.w0" "rig:UnTwistIKHip_R_poleVectorConstraint1.tg[0].tw"
		;
connectAttr "rig:TwistFollowParentHip_R_parentConstraint1.ctx" "rig:TwistFollowParentHip_R.tx"
		;
connectAttr "rig:TwistFollowParentHip_R_parentConstraint1.cty" "rig:TwistFollowParentHip_R.ty"
		;
connectAttr "rig:TwistFollowParentHip_R_parentConstraint1.ctz" "rig:TwistFollowParentHip_R.tz"
		;
connectAttr "rig:TwistFollowParentHip_R_parentConstraint1.crx" "rig:TwistFollowParentHip_R.rx"
		;
connectAttr "rig:TwistFollowParentHip_R_parentConstraint1.cry" "rig:TwistFollowParentHip_R.ry"
		;
connectAttr "rig:TwistFollowParentHip_R_parentConstraint1.crz" "rig:TwistFollowParentHip_R.rz"
		;
connectAttr "rig:TwistFollowParentHip_R.ro" "rig:TwistFollowParentHip_R_parentConstraint1.cro"
		;
connectAttr "rig:TwistFollowParentHip_R.pim" "rig:TwistFollowParentHip_R_parentConstraint1.cpim"
		;
connectAttr "rig:TwistFollowParentHip_R.rp" "rig:TwistFollowParentHip_R_parentConstraint1.crp"
		;
connectAttr "rig:TwistFollowParentHip_R.rpt" "rig:TwistFollowParentHip_R_parentConstraint1.crt"
		;
connectAttr "rig:FKXRoot_M.t" "rig:TwistFollowParentHip_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXRoot_M.rp" "rig:TwistFollowParentHip_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXRoot_M.rpt" "rig:TwistFollowParentHip_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXRoot_M.r" "rig:TwistFollowParentHip_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXRoot_M.ro" "rig:TwistFollowParentHip_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXRoot_M.s" "rig:TwistFollowParentHip_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXRoot_M.pm" "rig:TwistFollowParentHip_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXRoot_M.jo" "rig:TwistFollowParentHip_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistFollowParentHip_R_parentConstraint1.w0" "rig:TwistFollowParentHip_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendSpineReverse_M.ox" "rig:TwistFollowParentHip_R_parentConstraint1.w0"
		;
connectAttr "rig:UnTwistHip_R_pointConstraint1.ctx" "rig:UnTwistHip_R.tx";
connectAttr "rig:UnTwistHip_R_pointConstraint1.cty" "rig:UnTwistHip_R.ty";
connectAttr "rig:UnTwistHip_R_pointConstraint1.ctz" "rig:UnTwistHip_R.tz";
connectAttr "rig:UnTwistHip_R.s" "rig:UnTwistEndHip_R.is";
connectAttr "rig:UnTwistHip_R.pim" "rig:UnTwistHip_R_pointConstraint1.cpim";
connectAttr "rig:UnTwistHip_R.rp" "rig:UnTwistHip_R_pointConstraint1.crp";
connectAttr "rig:UnTwistHip_R.rpt" "rig:UnTwistHip_R_pointConstraint1.crt";
connectAttr "rig:FKXHip_R.t" "rig:UnTwistHip_R_pointConstraint1.tg[0].tt";
connectAttr "rig:FKXHip_R.rp" "rig:UnTwistHip_R_pointConstraint1.tg[0].trp";
connectAttr "rig:FKXHip_R.rpt" "rig:UnTwistHip_R_pointConstraint1.tg[0].trt";
connectAttr "rig:FKXHip_R.pm" "rig:UnTwistHip_R_pointConstraint1.tg[0].tpm";
connectAttr "rig:UnTwistHip_R_pointConstraint1.w0" "rig:UnTwistHip_R_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:UnTwistEndHip_R.tx" "rig:effector4.tx";
connectAttr "rig:UnTwistEndHip_R.ty" "rig:effector4.ty";
connectAttr "rig:UnTwistEndHip_R.tz" "rig:effector4.tz";
connectAttr "rig:UnTwistHip_R.s" "rig:TwistBalancerHip_R.is";
connectAttr "rig:TwistBalancerHip_R_parentConstraint1.ctx" "rig:TwistBalancerHip_R.tx"
		;
connectAttr "rig:TwistBalancerHip_R_parentConstraint1.cty" "rig:TwistBalancerHip_R.ty"
		;
connectAttr "rig:TwistBalancerHip_R_parentConstraint1.ctz" "rig:TwistBalancerHip_R.tz"
		;
connectAttr "rig:TwistBalancerHip_R_parentConstraint1.crx" "rig:TwistBalancerHip_R.rx"
		;
connectAttr "rig:TwistBalancerHip_R_parentConstraint1.cry" "rig:TwistBalancerHip_R.ry"
		;
connectAttr "rig:TwistBalancerHip_R_parentConstraint1.crz" "rig:TwistBalancerHip_R.rz"
		;
connectAttr "rig:TwistBalancerHip_R.ro" "rig:TwistBalancerHip_R_parentConstraint1.cro"
		;
connectAttr "rig:TwistBalancerHip_R.pim" "rig:TwistBalancerHip_R_parentConstraint1.cpim"
		;
connectAttr "rig:TwistBalancerHip_R.rp" "rig:TwistBalancerHip_R_parentConstraint1.crp"
		;
connectAttr "rig:TwistBalancerHip_R.rpt" "rig:TwistBalancerHip_R_parentConstraint1.crt"
		;
connectAttr "rig:TwistBalancerHip_R.jo" "rig:TwistBalancerHip_R_parentConstraint1.cjo"
		;
connectAttr "rig:FKXHip_R.t" "rig:TwistBalancerHip_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXHip_R.rp" "rig:TwistBalancerHip_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXHip_R.rpt" "rig:TwistBalancerHip_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXHip_R.r" "rig:TwistBalancerHip_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXHip_R.ro" "rig:TwistBalancerHip_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXHip_R.s" "rig:TwistBalancerHip_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXHip_R.pm" "rig:TwistBalancerHip_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXHip_R.jo" "rig:TwistBalancerHip_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistBalancerHip_R_parentConstraint1.w0" "rig:TwistBalancerHip_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:unitConversion37.o" "rig:TwisterHip0_R.rx";
connectAttr "rig:unitConversion39.o" "rig:TwisterHip1_R.rx";
connectAttr "rig:unitConversion41.o" "rig:TwisterHip2_R.rx";
connectAttr "rig:UnTwistWrist_R.msg" "rig:UnTwistIKWrist_R.hsj";
connectAttr "rig:effector5.hp" "rig:UnTwistIKWrist_R.hee";
connectAttr "rig:ikRPsolver.msg" "rig:UnTwistIKWrist_R.hsv";
connectAttr "rig:UnTwistIKWrist_R_poleVectorConstraint1.ctx" "rig:UnTwistIKWrist_R.pvx"
		;
connectAttr "rig:UnTwistIKWrist_R_poleVectorConstraint1.cty" "rig:UnTwistIKWrist_R.pvy"
		;
connectAttr "rig:UnTwistIKWrist_R_poleVectorConstraint1.ctz" "rig:UnTwistIKWrist_R.pvz"
		;
connectAttr "rig:UnTwistIKWrist_R.pim" "rig:UnTwistIKWrist_R_poleVectorConstraint1.cpim"
		;
connectAttr "rig:UnTwistWrist_R.pm" "rig:UnTwistIKWrist_R_poleVectorConstraint1.ps"
		;
connectAttr "rig:UnTwistWrist_R.t" "rig:UnTwistIKWrist_R_poleVectorConstraint1.crp"
		;
connectAttr "rig:UnTwistWrist_R.t" "rig:UnTwistIKWrist_R_poleVectorConstraint1.tg[0].tt"
		;
connectAttr "rig:UnTwistWrist_R.rp" "rig:UnTwistIKWrist_R_poleVectorConstraint1.tg[0].trp"
		;
connectAttr "rig:UnTwistWrist_R.rpt" "rig:UnTwistIKWrist_R_poleVectorConstraint1.tg[0].trt"
		;
connectAttr "rig:UnTwistWrist_R.pm" "rig:UnTwistIKWrist_R_poleVectorConstraint1.tg[0].tpm"
		;
connectAttr "rig:UnTwistIKWrist_R_poleVectorConstraint1.w0" "rig:UnTwistIKWrist_R_poleVectorConstraint1.tg[0].tw"
		;
connectAttr "rig:UnTwistWrist_R.s" "rig:UnTwistEndWrist_R.is";
connectAttr "rig:UnTwistEndWrist_R.tx" "rig:effector5.tx";
connectAttr "rig:UnTwistEndWrist_R.ty" "rig:effector5.ty";
connectAttr "rig:UnTwistEndWrist_R.tz" "rig:effector5.tz";
connectAttr "rig:UnTwistWrist_R.s" "rig:TwistBalancerWrist_R.is";
connectAttr "rig:unitConversion43.o" "rig:TwisterWrist0_R.rx";
connectAttr "rig:unitConversion45.o" "rig:TwisterWrist1_R.rx";
connectAttr "rig:unitConversion47.o" "rig:TwisterWrist2_R.rx";
connectAttr "rig:UnTwistElbow_R.msg" "rig:UnTwistIKElbow_R.hsj";
connectAttr "rig:effector6.hp" "rig:UnTwistIKElbow_R.hee";
connectAttr "rig:ikRPsolver.msg" "rig:UnTwistIKElbow_R.hsv";
connectAttr "rig:UnTwistIKElbow_R_poleVectorConstraint1.ctx" "rig:UnTwistIKElbow_R.pvx"
		;
connectAttr "rig:UnTwistIKElbow_R_poleVectorConstraint1.cty" "rig:UnTwistIKElbow_R.pvy"
		;
connectAttr "rig:UnTwistIKElbow_R_poleVectorConstraint1.ctz" "rig:UnTwistIKElbow_R.pvz"
		;
connectAttr "rig:UnTwistIKElbow_R.pim" "rig:UnTwistIKElbow_R_poleVectorConstraint1.cpim"
		;
connectAttr "rig:UnTwistElbow_R.pm" "rig:UnTwistIKElbow_R_poleVectorConstraint1.ps"
		;
connectAttr "rig:UnTwistElbow_R.t" "rig:UnTwistIKElbow_R_poleVectorConstraint1.crp"
		;
connectAttr "rig:UnTwistElbow_R.t" "rig:UnTwistIKElbow_R_poleVectorConstraint1.tg[0].tt"
		;
connectAttr "rig:UnTwistElbow_R.rp" "rig:UnTwistIKElbow_R_poleVectorConstraint1.tg[0].trp"
		;
connectAttr "rig:UnTwistElbow_R.rpt" "rig:UnTwistIKElbow_R_poleVectorConstraint1.tg[0].trt"
		;
connectAttr "rig:UnTwistElbow_R.pm" "rig:UnTwistIKElbow_R_poleVectorConstraint1.tg[0].tpm"
		;
connectAttr "rig:UnTwistIKElbow_R_poleVectorConstraint1.w0" "rig:UnTwistIKElbow_R_poleVectorConstraint1.tg[0].tw"
		;
connectAttr "rig:UnTwistElbow_R.s" "rig:UnTwistEndElbow_R.is";
connectAttr "rig:UnTwistEndElbow_R.tx" "rig:effector6.tx";
connectAttr "rig:UnTwistEndElbow_R.ty" "rig:effector6.ty";
connectAttr "rig:UnTwistEndElbow_R.tz" "rig:effector6.tz";
connectAttr "rig:UnTwistElbow_R.s" "rig:TwistBalancerElbow_R.is";
connectAttr "rig:unitConversion49.o" "rig:TwisterElbow0_R.rx";
connectAttr "rig:unitConversion51.o" "rig:TwisterElbow1_R.rx";
connectAttr "rig:unitConversion53.o" "rig:TwisterElbow2_R.rx";
connectAttr "rig:UnTwistShoulder_R.msg" "rig:UnTwistIKShoulder_R.hsj";
connectAttr "rig:effector7.hp" "rig:UnTwistIKShoulder_R.hee";
connectAttr "rig:ikRPsolver.msg" "rig:UnTwistIKShoulder_R.hsv";
connectAttr "rig:UnTwistIKShoulder_R_poleVectorConstraint1.ctx" "rig:UnTwistIKShoulder_R.pvx"
		;
connectAttr "rig:UnTwistIKShoulder_R_poleVectorConstraint1.cty" "rig:UnTwistIKShoulder_R.pvy"
		;
connectAttr "rig:UnTwistIKShoulder_R_poleVectorConstraint1.ctz" "rig:UnTwistIKShoulder_R.pvz"
		;
connectAttr "rig:UnTwistIKShoulder_R.pim" "rig:UnTwistIKShoulder_R_poleVectorConstraint1.cpim"
		;
connectAttr "rig:UnTwistShoulder_R.pm" "rig:UnTwistIKShoulder_R_poleVectorConstraint1.ps"
		;
connectAttr "rig:UnTwistShoulder_R.t" "rig:UnTwistIKShoulder_R_poleVectorConstraint1.crp"
		;
connectAttr "rig:UnTwistShoulder_R.t" "rig:UnTwistIKShoulder_R_poleVectorConstraint1.tg[0].tt"
		;
connectAttr "rig:UnTwistShoulder_R.rp" "rig:UnTwistIKShoulder_R_poleVectorConstraint1.tg[0].trp"
		;
connectAttr "rig:UnTwistShoulder_R.rpt" "rig:UnTwistIKShoulder_R_poleVectorConstraint1.tg[0].trt"
		;
connectAttr "rig:UnTwistShoulder_R.pm" "rig:UnTwistIKShoulder_R_poleVectorConstraint1.tg[0].tpm"
		;
connectAttr "rig:UnTwistIKShoulder_R_poleVectorConstraint1.w0" "rig:UnTwistIKShoulder_R_poleVectorConstraint1.tg[0].tw"
		;
connectAttr "rig:UnTwistShoulder_R.s" "rig:UnTwistEndShoulder_R.is";
connectAttr "rig:UnTwistEndShoulder_R.tx" "rig:effector7.tx";
connectAttr "rig:UnTwistEndShoulder_R.ty" "rig:effector7.ty";
connectAttr "rig:UnTwistEndShoulder_R.tz" "rig:effector7.tz";
connectAttr "rig:UnTwistShoulder_R.s" "rig:TwistBalancerShoulder_R.is";
connectAttr "rig:unitConversion55.o" "rig:TwisterShoulder0_R.rx";
connectAttr "rig:unitConversion57.o" "rig:TwisterShoulder1_R.rx";
connectAttr "rig:unitConversion59.o" "rig:TwisterShoulder2_R.rx";
connectAttr "rig:TwistFollowKnee_L_parentConstraint1.ctx" "rig:TwistFollowKnee_L.tx"
		;
connectAttr "rig:TwistFollowKnee_L_parentConstraint1.cty" "rig:TwistFollowKnee_L.ty"
		;
connectAttr "rig:TwistFollowKnee_L_parentConstraint1.ctz" "rig:TwistFollowKnee_L.tz"
		;
connectAttr "rig:TwistFollowKnee_L_parentConstraint1.crx" "rig:TwistFollowKnee_L.rx"
		;
connectAttr "rig:TwistFollowKnee_L_parentConstraint1.cry" "rig:TwistFollowKnee_L.ry"
		;
connectAttr "rig:TwistFollowKnee_L_parentConstraint1.crz" "rig:TwistFollowKnee_L.rz"
		;
connectAttr "rig:TwistFollowKnee_L.ro" "rig:TwistFollowKnee_L_parentConstraint1.cro"
		;
connectAttr "rig:TwistFollowKnee_L.pim" "rig:TwistFollowKnee_L_parentConstraint1.cpim"
		;
connectAttr "rig:TwistFollowKnee_L.rp" "rig:TwistFollowKnee_L_parentConstraint1.crp"
		;
connectAttr "rig:TwistFollowKnee_L.rpt" "rig:TwistFollowKnee_L_parentConstraint1.crt"
		;
connectAttr "rig:FKXKnee_L.t" "rig:TwistFollowKnee_L_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXKnee_L.rp" "rig:TwistFollowKnee_L_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXKnee_L.rpt" "rig:TwistFollowKnee_L_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXKnee_L.r" "rig:TwistFollowKnee_L_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXKnee_L.ro" "rig:TwistFollowKnee_L_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXKnee_L.s" "rig:TwistFollowKnee_L_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXKnee_L.pm" "rig:TwistFollowKnee_L_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXKnee_L.jo" "rig:TwistFollowKnee_L_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistFollowKnee_L_parentConstraint1.w0" "rig:TwistFollowKnee_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:UnTwistKnee_L.msg" "rig:UnTwistIKKnee_L.hsj";
connectAttr "rig:effector8.hp" "rig:UnTwistIKKnee_L.hee";
connectAttr "rig:ikRPsolver.msg" "rig:UnTwistIKKnee_L.hsv";
connectAttr "rig:UnTwistIKKnee_L_poleVectorConstraint1.ctx" "rig:UnTwistIKKnee_L.pvx"
		;
connectAttr "rig:UnTwistIKKnee_L_poleVectorConstraint1.cty" "rig:UnTwistIKKnee_L.pvy"
		;
connectAttr "rig:UnTwistIKKnee_L_poleVectorConstraint1.ctz" "rig:UnTwistIKKnee_L.pvz"
		;
connectAttr "rig:UnTwistIKKnee_L.pim" "rig:UnTwistIKKnee_L_poleVectorConstraint1.cpim"
		;
connectAttr "rig:UnTwistKnee_L.pm" "rig:UnTwistIKKnee_L_poleVectorConstraint1.ps"
		;
connectAttr "rig:UnTwistKnee_L.t" "rig:UnTwistIKKnee_L_poleVectorConstraint1.crp"
		;
connectAttr "rig:UnTwistKnee_L.t" "rig:UnTwistIKKnee_L_poleVectorConstraint1.tg[0].tt"
		;
connectAttr "rig:UnTwistKnee_L.rp" "rig:UnTwistIKKnee_L_poleVectorConstraint1.tg[0].trp"
		;
connectAttr "rig:UnTwistKnee_L.rpt" "rig:UnTwistIKKnee_L_poleVectorConstraint1.tg[0].trt"
		;
connectAttr "rig:UnTwistKnee_L.pm" "rig:UnTwistIKKnee_L_poleVectorConstraint1.tg[0].tpm"
		;
connectAttr "rig:UnTwistIKKnee_L_poleVectorConstraint1.w0" "rig:UnTwistIKKnee_L_poleVectorConstraint1.tg[0].tw"
		;
connectAttr "rig:TwistFollowParentKnee_L_parentConstraint1.ctx" "rig:TwistFollowParentKnee_L.tx"
		;
connectAttr "rig:TwistFollowParentKnee_L_parentConstraint1.cty" "rig:TwistFollowParentKnee_L.ty"
		;
connectAttr "rig:TwistFollowParentKnee_L_parentConstraint1.ctz" "rig:TwistFollowParentKnee_L.tz"
		;
connectAttr "rig:TwistFollowParentKnee_L_parentConstraint1.crx" "rig:TwistFollowParentKnee_L.rx"
		;
connectAttr "rig:TwistFollowParentKnee_L_parentConstraint1.cry" "rig:TwistFollowParentKnee_L.ry"
		;
connectAttr "rig:TwistFollowParentKnee_L_parentConstraint1.crz" "rig:TwistFollowParentKnee_L.rz"
		;
connectAttr "rig:TwistFollowParentKnee_L.ro" "rig:TwistFollowParentKnee_L_parentConstraint1.cro"
		;
connectAttr "rig:TwistFollowParentKnee_L.pim" "rig:TwistFollowParentKnee_L_parentConstraint1.cpim"
		;
connectAttr "rig:TwistFollowParentKnee_L.rp" "rig:TwistFollowParentKnee_L_parentConstraint1.crp"
		;
connectAttr "rig:TwistFollowParentKnee_L.rpt" "rig:TwistFollowParentKnee_L_parentConstraint1.crt"
		;
connectAttr "rig:FKXHip_L.t" "rig:TwistFollowParentKnee_L_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXHip_L.rp" "rig:TwistFollowParentKnee_L_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXHip_L.rpt" "rig:TwistFollowParentKnee_L_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXHip_L.r" "rig:TwistFollowParentKnee_L_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXHip_L.ro" "rig:TwistFollowParentKnee_L_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXHip_L.s" "rig:TwistFollowParentKnee_L_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXHip_L.pm" "rig:TwistFollowParentKnee_L_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXHip_L.jo" "rig:TwistFollowParentKnee_L_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistFollowParentKnee_L_parentConstraint1.w0" "rig:TwistFollowParentKnee_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:UnTwistKnee_L_pointConstraint1.ctx" "rig:UnTwistKnee_L.tx";
connectAttr "rig:UnTwistKnee_L_pointConstraint1.cty" "rig:UnTwistKnee_L.ty";
connectAttr "rig:UnTwistKnee_L_pointConstraint1.ctz" "rig:UnTwistKnee_L.tz";
connectAttr "rig:UnTwistKnee_L.s" "rig:UnTwistEndKnee_L.is";
connectAttr "rig:UnTwistKnee_L.pim" "rig:UnTwistKnee_L_pointConstraint1.cpim";
connectAttr "rig:UnTwistKnee_L.rp" "rig:UnTwistKnee_L_pointConstraint1.crp";
connectAttr "rig:UnTwistKnee_L.rpt" "rig:UnTwistKnee_L_pointConstraint1.crt";
connectAttr "rig:FKXKnee_L.t" "rig:UnTwistKnee_L_pointConstraint1.tg[0].tt";
connectAttr "rig:FKXKnee_L.rp" "rig:UnTwistKnee_L_pointConstraint1.tg[0].trp";
connectAttr "rig:FKXKnee_L.rpt" "rig:UnTwistKnee_L_pointConstraint1.tg[0].trt";
connectAttr "rig:FKXKnee_L.pm" "rig:UnTwistKnee_L_pointConstraint1.tg[0].tpm";
connectAttr "rig:UnTwistKnee_L_pointConstraint1.w0" "rig:UnTwistKnee_L_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:UnTwistEndKnee_L.tx" "rig:effector8.tx";
connectAttr "rig:UnTwistEndKnee_L.ty" "rig:effector8.ty";
connectAttr "rig:UnTwistEndKnee_L.tz" "rig:effector8.tz";
connectAttr "rig:UnTwistKnee_L.s" "rig:TwistBalancerKnee_L.is";
connectAttr "rig:TwistBalancerKnee_L_parentConstraint1.ctx" "rig:TwistBalancerKnee_L.tx"
		;
connectAttr "rig:TwistBalancerKnee_L_parentConstraint1.cty" "rig:TwistBalancerKnee_L.ty"
		;
connectAttr "rig:TwistBalancerKnee_L_parentConstraint1.ctz" "rig:TwistBalancerKnee_L.tz"
		;
connectAttr "rig:TwistBalancerKnee_L_parentConstraint1.crx" "rig:TwistBalancerKnee_L.rx"
		;
connectAttr "rig:TwistBalancerKnee_L_parentConstraint1.cry" "rig:TwistBalancerKnee_L.ry"
		;
connectAttr "rig:TwistBalancerKnee_L_parentConstraint1.crz" "rig:TwistBalancerKnee_L.rz"
		;
connectAttr "rig:TwistBalancerKnee_L.ro" "rig:TwistBalancerKnee_L_parentConstraint1.cro"
		;
connectAttr "rig:TwistBalancerKnee_L.pim" "rig:TwistBalancerKnee_L_parentConstraint1.cpim"
		;
connectAttr "rig:TwistBalancerKnee_L.rp" "rig:TwistBalancerKnee_L_parentConstraint1.crp"
		;
connectAttr "rig:TwistBalancerKnee_L.rpt" "rig:TwistBalancerKnee_L_parentConstraint1.crt"
		;
connectAttr "rig:TwistBalancerKnee_L.jo" "rig:TwistBalancerKnee_L_parentConstraint1.cjo"
		;
connectAttr "rig:FKXKnee_L.t" "rig:TwistBalancerKnee_L_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXKnee_L.rp" "rig:TwistBalancerKnee_L_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXKnee_L.rpt" "rig:TwistBalancerKnee_L_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXKnee_L.r" "rig:TwistBalancerKnee_L_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXKnee_L.ro" "rig:TwistBalancerKnee_L_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXKnee_L.s" "rig:TwistBalancerKnee_L_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXKnee_L.pm" "rig:TwistBalancerKnee_L_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXKnee_L.jo" "rig:TwistBalancerKnee_L_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistBalancerKnee_L_parentConstraint1.w0" "rig:TwistBalancerKnee_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:unitConversion61.o" "rig:TwisterKnee0_L.rx";
connectAttr "rig:unitConversion63.o" "rig:TwisterKnee1_L.rx";
connectAttr "rig:unitConversion65.o" "rig:TwisterKnee2_L.rx";
connectAttr "rig:TwistFollowHip_L_parentConstraint1.ctx" "rig:TwistFollowHip_L.tx"
		;
connectAttr "rig:TwistFollowHip_L_parentConstraint1.cty" "rig:TwistFollowHip_L.ty"
		;
connectAttr "rig:TwistFollowHip_L_parentConstraint1.ctz" "rig:TwistFollowHip_L.tz"
		;
connectAttr "rig:TwistFollowHip_L_parentConstraint1.crx" "rig:TwistFollowHip_L.rx"
		;
connectAttr "rig:TwistFollowHip_L_parentConstraint1.cry" "rig:TwistFollowHip_L.ry"
		;
connectAttr "rig:TwistFollowHip_L_parentConstraint1.crz" "rig:TwistFollowHip_L.rz"
		;
connectAttr "rig:TwistFollowHip_L.ro" "rig:TwistFollowHip_L_parentConstraint1.cro"
		;
connectAttr "rig:TwistFollowHip_L.pim" "rig:TwistFollowHip_L_parentConstraint1.cpim"
		;
connectAttr "rig:TwistFollowHip_L.rp" "rig:TwistFollowHip_L_parentConstraint1.crp"
		;
connectAttr "rig:TwistFollowHip_L.rpt" "rig:TwistFollowHip_L_parentConstraint1.crt"
		;
connectAttr "rig:FKXHip_L.t" "rig:TwistFollowHip_L_parentConstraint1.tg[0].tt";
connectAttr "rig:FKXHip_L.rp" "rig:TwistFollowHip_L_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXHip_L.rpt" "rig:TwistFollowHip_L_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXHip_L.r" "rig:TwistFollowHip_L_parentConstraint1.tg[0].tr";
connectAttr "rig:FKXHip_L.ro" "rig:TwistFollowHip_L_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXHip_L.s" "rig:TwistFollowHip_L_parentConstraint1.tg[0].ts";
connectAttr "rig:FKXHip_L.pm" "rig:TwistFollowHip_L_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXHip_L.jo" "rig:TwistFollowHip_L_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistFollowHip_L_parentConstraint1.w0" "rig:TwistFollowHip_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:UnTwistHip_L.msg" "rig:UnTwistIKHip_L.hsj";
connectAttr "rig:effector9.hp" "rig:UnTwistIKHip_L.hee";
connectAttr "rig:ikRPsolver.msg" "rig:UnTwistIKHip_L.hsv";
connectAttr "rig:UnTwistIKHip_L_poleVectorConstraint1.ctx" "rig:UnTwistIKHip_L.pvx"
		;
connectAttr "rig:UnTwistIKHip_L_poleVectorConstraint1.cty" "rig:UnTwistIKHip_L.pvy"
		;
connectAttr "rig:UnTwistIKHip_L_poleVectorConstraint1.ctz" "rig:UnTwistIKHip_L.pvz"
		;
connectAttr "rig:UnTwistIKHip_L.pim" "rig:UnTwistIKHip_L_poleVectorConstraint1.cpim"
		;
connectAttr "rig:UnTwistHip_L.pm" "rig:UnTwistIKHip_L_poleVectorConstraint1.ps";
connectAttr "rig:UnTwistHip_L.t" "rig:UnTwistIKHip_L_poleVectorConstraint1.crp";
connectAttr "rig:UnTwistHip_L.t" "rig:UnTwistIKHip_L_poleVectorConstraint1.tg[0].tt"
		;
connectAttr "rig:UnTwistHip_L.rp" "rig:UnTwistIKHip_L_poleVectorConstraint1.tg[0].trp"
		;
connectAttr "rig:UnTwistHip_L.rpt" "rig:UnTwistIKHip_L_poleVectorConstraint1.tg[0].trt"
		;
connectAttr "rig:UnTwistHip_L.pm" "rig:UnTwistIKHip_L_poleVectorConstraint1.tg[0].tpm"
		;
connectAttr "rig:UnTwistIKHip_L_poleVectorConstraint1.w0" "rig:UnTwistIKHip_L_poleVectorConstraint1.tg[0].tw"
		;
connectAttr "rig:TwistFollowParentHip_L_parentConstraint1.ctx" "rig:TwistFollowParentHip_L.tx"
		;
connectAttr "rig:TwistFollowParentHip_L_parentConstraint1.cty" "rig:TwistFollowParentHip_L.ty"
		;
connectAttr "rig:TwistFollowParentHip_L_parentConstraint1.ctz" "rig:TwistFollowParentHip_L.tz"
		;
connectAttr "rig:TwistFollowParentHip_L_parentConstraint1.crx" "rig:TwistFollowParentHip_L.rx"
		;
connectAttr "rig:TwistFollowParentHip_L_parentConstraint1.cry" "rig:TwistFollowParentHip_L.ry"
		;
connectAttr "rig:TwistFollowParentHip_L_parentConstraint1.crz" "rig:TwistFollowParentHip_L.rz"
		;
connectAttr "rig:TwistFollowParentHip_L.ro" "rig:TwistFollowParentHip_L_parentConstraint1.cro"
		;
connectAttr "rig:TwistFollowParentHip_L.pim" "rig:TwistFollowParentHip_L_parentConstraint1.cpim"
		;
connectAttr "rig:TwistFollowParentHip_L.rp" "rig:TwistFollowParentHip_L_parentConstraint1.crp"
		;
connectAttr "rig:TwistFollowParentHip_L.rpt" "rig:TwistFollowParentHip_L_parentConstraint1.crt"
		;
connectAttr "rig:FKXRoot_M.t" "rig:TwistFollowParentHip_L_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXRoot_M.rp" "rig:TwistFollowParentHip_L_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXRoot_M.rpt" "rig:TwistFollowParentHip_L_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXRoot_M.r" "rig:TwistFollowParentHip_L_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXRoot_M.ro" "rig:TwistFollowParentHip_L_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXRoot_M.s" "rig:TwistFollowParentHip_L_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXRoot_M.pm" "rig:TwistFollowParentHip_L_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXRoot_M.jo" "rig:TwistFollowParentHip_L_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistFollowParentHip_L_parentConstraint1.w0" "rig:TwistFollowParentHip_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendSpineReverse_M.ox" "rig:TwistFollowParentHip_L_parentConstraint1.w0"
		;
connectAttr "rig:UnTwistHip_L_pointConstraint1.ctx" "rig:UnTwistHip_L.tx";
connectAttr "rig:UnTwistHip_L_pointConstraint1.cty" "rig:UnTwistHip_L.ty";
connectAttr "rig:UnTwistHip_L_pointConstraint1.ctz" "rig:UnTwistHip_L.tz";
connectAttr "rig:UnTwistHip_L.s" "rig:UnTwistEndHip_L.is";
connectAttr "rig:UnTwistHip_L.pim" "rig:UnTwistHip_L_pointConstraint1.cpim";
connectAttr "rig:UnTwistHip_L.rp" "rig:UnTwistHip_L_pointConstraint1.crp";
connectAttr "rig:UnTwistHip_L.rpt" "rig:UnTwistHip_L_pointConstraint1.crt";
connectAttr "rig:FKXHip_L.t" "rig:UnTwistHip_L_pointConstraint1.tg[0].tt";
connectAttr "rig:FKXHip_L.rp" "rig:UnTwistHip_L_pointConstraint1.tg[0].trp";
connectAttr "rig:FKXHip_L.rpt" "rig:UnTwistHip_L_pointConstraint1.tg[0].trt";
connectAttr "rig:FKXHip_L.pm" "rig:UnTwistHip_L_pointConstraint1.tg[0].tpm";
connectAttr "rig:UnTwistHip_L_pointConstraint1.w0" "rig:UnTwistHip_L_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:UnTwistEndHip_L.tx" "rig:effector9.tx";
connectAttr "rig:UnTwistEndHip_L.ty" "rig:effector9.ty";
connectAttr "rig:UnTwistEndHip_L.tz" "rig:effector9.tz";
connectAttr "rig:UnTwistHip_L.s" "rig:TwistBalancerHip_L.is";
connectAttr "rig:TwistBalancerHip_L_parentConstraint1.ctx" "rig:TwistBalancerHip_L.tx"
		;
connectAttr "rig:TwistBalancerHip_L_parentConstraint1.cty" "rig:TwistBalancerHip_L.ty"
		;
connectAttr "rig:TwistBalancerHip_L_parentConstraint1.ctz" "rig:TwistBalancerHip_L.tz"
		;
connectAttr "rig:TwistBalancerHip_L_parentConstraint1.crx" "rig:TwistBalancerHip_L.rx"
		;
connectAttr "rig:TwistBalancerHip_L_parentConstraint1.cry" "rig:TwistBalancerHip_L.ry"
		;
connectAttr "rig:TwistBalancerHip_L_parentConstraint1.crz" "rig:TwistBalancerHip_L.rz"
		;
connectAttr "rig:TwistBalancerHip_L.ro" "rig:TwistBalancerHip_L_parentConstraint1.cro"
		;
connectAttr "rig:TwistBalancerHip_L.pim" "rig:TwistBalancerHip_L_parentConstraint1.cpim"
		;
connectAttr "rig:TwistBalancerHip_L.rp" "rig:TwistBalancerHip_L_parentConstraint1.crp"
		;
connectAttr "rig:TwistBalancerHip_L.rpt" "rig:TwistBalancerHip_L_parentConstraint1.crt"
		;
connectAttr "rig:TwistBalancerHip_L.jo" "rig:TwistBalancerHip_L_parentConstraint1.cjo"
		;
connectAttr "rig:FKXHip_L.t" "rig:TwistBalancerHip_L_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXHip_L.rp" "rig:TwistBalancerHip_L_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXHip_L.rpt" "rig:TwistBalancerHip_L_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXHip_L.r" "rig:TwistBalancerHip_L_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXHip_L.ro" "rig:TwistBalancerHip_L_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXHip_L.s" "rig:TwistBalancerHip_L_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXHip_L.pm" "rig:TwistBalancerHip_L_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXHip_L.jo" "rig:TwistBalancerHip_L_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistBalancerHip_L_parentConstraint1.w0" "rig:TwistBalancerHip_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:unitConversion67.o" "rig:TwisterHip0_L.rx";
connectAttr "rig:unitConversion69.o" "rig:TwisterHip1_L.rx";
connectAttr "rig:unitConversion71.o" "rig:TwisterHip2_L.rx";
connectAttr "rig:TwistFollowWrist_L_parentConstraint1.ctx" "rig:TwistFollowWrist_L.tx"
		;
connectAttr "rig:TwistFollowWrist_L_parentConstraint1.cty" "rig:TwistFollowWrist_L.ty"
		;
connectAttr "rig:TwistFollowWrist_L_parentConstraint1.ctz" "rig:TwistFollowWrist_L.tz"
		;
connectAttr "rig:TwistFollowWrist_L_parentConstraint1.crx" "rig:TwistFollowWrist_L.rx"
		;
connectAttr "rig:TwistFollowWrist_L_parentConstraint1.cry" "rig:TwistFollowWrist_L.ry"
		;
connectAttr "rig:TwistFollowWrist_L_parentConstraint1.crz" "rig:TwistFollowWrist_L.rz"
		;
connectAttr "rig:TwistFollowWrist_L.ro" "rig:TwistFollowWrist_L_parentConstraint1.cro"
		;
connectAttr "rig:TwistFollowWrist_L.pim" "rig:TwistFollowWrist_L_parentConstraint1.cpim"
		;
connectAttr "rig:TwistFollowWrist_L.rp" "rig:TwistFollowWrist_L_parentConstraint1.crp"
		;
connectAttr "rig:TwistFollowWrist_L.rpt" "rig:TwistFollowWrist_L_parentConstraint1.crt"
		;
connectAttr "rig:FKXWrist_L.t" "rig:TwistFollowWrist_L_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXWrist_L.rp" "rig:TwistFollowWrist_L_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXWrist_L.rpt" "rig:TwistFollowWrist_L_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXWrist_L.r" "rig:TwistFollowWrist_L_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXWrist_L.ro" "rig:TwistFollowWrist_L_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXWrist_L.s" "rig:TwistFollowWrist_L_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXWrist_L.pm" "rig:TwistFollowWrist_L_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXWrist_L.jo" "rig:TwistFollowWrist_L_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistFollowWrist_L_parentConstraint1.w0" "rig:TwistFollowWrist_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendArmReverse_L.ox" "rig:TwistFollowWrist_L_parentConstraint1.w0"
		;
connectAttr "rig:UnTwistWrist_L.msg" "rig:UnTwistIKWrist_L.hsj";
connectAttr "rig:effector10.hp" "rig:UnTwistIKWrist_L.hee";
connectAttr "rig:ikRPsolver.msg" "rig:UnTwistIKWrist_L.hsv";
connectAttr "rig:UnTwistIKWrist_L_poleVectorConstraint1.ctx" "rig:UnTwistIKWrist_L.pvx"
		;
connectAttr "rig:UnTwistIKWrist_L_poleVectorConstraint1.cty" "rig:UnTwistIKWrist_L.pvy"
		;
connectAttr "rig:UnTwistIKWrist_L_poleVectorConstraint1.ctz" "rig:UnTwistIKWrist_L.pvz"
		;
connectAttr "rig:UnTwistIKWrist_L.pim" "rig:UnTwistIKWrist_L_poleVectorConstraint1.cpim"
		;
connectAttr "rig:UnTwistWrist_L.pm" "rig:UnTwistIKWrist_L_poleVectorConstraint1.ps"
		;
connectAttr "rig:UnTwistWrist_L.t" "rig:UnTwistIKWrist_L_poleVectorConstraint1.crp"
		;
connectAttr "rig:UnTwistWrist_L.t" "rig:UnTwistIKWrist_L_poleVectorConstraint1.tg[0].tt"
		;
connectAttr "rig:UnTwistWrist_L.rp" "rig:UnTwistIKWrist_L_poleVectorConstraint1.tg[0].trp"
		;
connectAttr "rig:UnTwistWrist_L.rpt" "rig:UnTwistIKWrist_L_poleVectorConstraint1.tg[0].trt"
		;
connectAttr "rig:UnTwistWrist_L.pm" "rig:UnTwistIKWrist_L_poleVectorConstraint1.tg[0].tpm"
		;
connectAttr "rig:UnTwistIKWrist_L_poleVectorConstraint1.w0" "rig:UnTwistIKWrist_L_poleVectorConstraint1.tg[0].tw"
		;
connectAttr "rig:TwistFollowParentWrist_L_parentConstraint1.ctx" "rig:TwistFollowParentWrist_L.tx"
		;
connectAttr "rig:TwistFollowParentWrist_L_parentConstraint1.cty" "rig:TwistFollowParentWrist_L.ty"
		;
connectAttr "rig:TwistFollowParentWrist_L_parentConstraint1.ctz" "rig:TwistFollowParentWrist_L.tz"
		;
connectAttr "rig:TwistFollowParentWrist_L_parentConstraint1.crx" "rig:TwistFollowParentWrist_L.rx"
		;
connectAttr "rig:TwistFollowParentWrist_L_parentConstraint1.cry" "rig:TwistFollowParentWrist_L.ry"
		;
connectAttr "rig:TwistFollowParentWrist_L_parentConstraint1.crz" "rig:TwistFollowParentWrist_L.rz"
		;
connectAttr "rig:TwistFollowParentWrist_L.ro" "rig:TwistFollowParentWrist_L_parentConstraint1.cro"
		;
connectAttr "rig:TwistFollowParentWrist_L.pim" "rig:TwistFollowParentWrist_L_parentConstraint1.cpim"
		;
connectAttr "rig:TwistFollowParentWrist_L.rp" "rig:TwistFollowParentWrist_L_parentConstraint1.crp"
		;
connectAttr "rig:TwistFollowParentWrist_L.rpt" "rig:TwistFollowParentWrist_L_parentConstraint1.crt"
		;
connectAttr "rig:FKXElbow_L.t" "rig:TwistFollowParentWrist_L_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXElbow_L.rp" "rig:TwistFollowParentWrist_L_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXElbow_L.rpt" "rig:TwistFollowParentWrist_L_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXElbow_L.r" "rig:TwistFollowParentWrist_L_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXElbow_L.ro" "rig:TwistFollowParentWrist_L_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXElbow_L.s" "rig:TwistFollowParentWrist_L_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXElbow_L.pm" "rig:TwistFollowParentWrist_L_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXElbow_L.jo" "rig:TwistFollowParentWrist_L_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistFollowParentWrist_L_parentConstraint1.w0" "rig:TwistFollowParentWrist_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendArmReverse_L.ox" "rig:TwistFollowParentWrist_L_parentConstraint1.w0"
		;
connectAttr "rig:UnTwistWrist_L_pointConstraint1.ctx" "rig:UnTwistWrist_L.tx";
connectAttr "rig:UnTwistWrist_L_pointConstraint1.cty" "rig:UnTwistWrist_L.ty";
connectAttr "rig:UnTwistWrist_L_pointConstraint1.ctz" "rig:UnTwistWrist_L.tz";
connectAttr "rig:UnTwistWrist_L.s" "rig:UnTwistEndWrist_L.is";
connectAttr "rig:UnTwistWrist_L.pim" "rig:UnTwistWrist_L_pointConstraint1.cpim";
connectAttr "rig:UnTwistWrist_L.rp" "rig:UnTwistWrist_L_pointConstraint1.crp";
connectAttr "rig:UnTwistWrist_L.rpt" "rig:UnTwistWrist_L_pointConstraint1.crt";
connectAttr "rig:FKXWrist_L.t" "rig:UnTwistWrist_L_pointConstraint1.tg[0].tt";
connectAttr "rig:FKXWrist_L.rp" "rig:UnTwistWrist_L_pointConstraint1.tg[0].trp";
connectAttr "rig:FKXWrist_L.rpt" "rig:UnTwistWrist_L_pointConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXWrist_L.pm" "rig:UnTwistWrist_L_pointConstraint1.tg[0].tpm";
connectAttr "rig:UnTwistWrist_L_pointConstraint1.w0" "rig:UnTwistWrist_L_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendArmReverse_L.ox" "rig:UnTwistWrist_L_pointConstraint1.w0"
		;
connectAttr "rig:UnTwistEndWrist_L.tx" "rig:effector10.tx";
connectAttr "rig:UnTwistEndWrist_L.ty" "rig:effector10.ty";
connectAttr "rig:UnTwistEndWrist_L.tz" "rig:effector10.tz";
connectAttr "rig:UnTwistWrist_L.s" "rig:TwistBalancerWrist_L.is";
connectAttr "rig:TwistBalancerWrist_L_parentConstraint1.ctx" "rig:TwistBalancerWrist_L.tx"
		;
connectAttr "rig:TwistBalancerWrist_L_parentConstraint1.cty" "rig:TwistBalancerWrist_L.ty"
		;
connectAttr "rig:TwistBalancerWrist_L_parentConstraint1.ctz" "rig:TwistBalancerWrist_L.tz"
		;
connectAttr "rig:TwistBalancerWrist_L_parentConstraint1.crx" "rig:TwistBalancerWrist_L.rx"
		;
connectAttr "rig:TwistBalancerWrist_L_parentConstraint1.cry" "rig:TwistBalancerWrist_L.ry"
		;
connectAttr "rig:TwistBalancerWrist_L_parentConstraint1.crz" "rig:TwistBalancerWrist_L.rz"
		;
connectAttr "rig:TwistBalancerWrist_L.ro" "rig:TwistBalancerWrist_L_parentConstraint1.cro"
		;
connectAttr "rig:TwistBalancerWrist_L.pim" "rig:TwistBalancerWrist_L_parentConstraint1.cpim"
		;
connectAttr "rig:TwistBalancerWrist_L.rp" "rig:TwistBalancerWrist_L_parentConstraint1.crp"
		;
connectAttr "rig:TwistBalancerWrist_L.rpt" "rig:TwistBalancerWrist_L_parentConstraint1.crt"
		;
connectAttr "rig:TwistBalancerWrist_L.jo" "rig:TwistBalancerWrist_L_parentConstraint1.cjo"
		;
connectAttr "rig:FKXWrist_L.t" "rig:TwistBalancerWrist_L_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXWrist_L.rp" "rig:TwistBalancerWrist_L_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXWrist_L.rpt" "rig:TwistBalancerWrist_L_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXWrist_L.r" "rig:TwistBalancerWrist_L_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXWrist_L.ro" "rig:TwistBalancerWrist_L_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXWrist_L.s" "rig:TwistBalancerWrist_L_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXWrist_L.pm" "rig:TwistBalancerWrist_L_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXWrist_L.jo" "rig:TwistBalancerWrist_L_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistBalancerWrist_L_parentConstraint1.w0" "rig:TwistBalancerWrist_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendArmReverse_L.ox" "rig:TwistBalancerWrist_L_parentConstraint1.w0"
		;
connectAttr "rig:unitConversion73.o" "rig:TwisterWrist0_L.rx";
connectAttr "rig:unitConversion75.o" "rig:TwisterWrist1_L.rx";
connectAttr "rig:unitConversion77.o" "rig:TwisterWrist2_L.rx";
connectAttr "rig:TwistFollowElbow_L_parentConstraint1.ctx" "rig:TwistFollowElbow_L.tx"
		;
connectAttr "rig:TwistFollowElbow_L_parentConstraint1.cty" "rig:TwistFollowElbow_L.ty"
		;
connectAttr "rig:TwistFollowElbow_L_parentConstraint1.ctz" "rig:TwistFollowElbow_L.tz"
		;
connectAttr "rig:TwistFollowElbow_L_parentConstraint1.crx" "rig:TwistFollowElbow_L.rx"
		;
connectAttr "rig:TwistFollowElbow_L_parentConstraint1.cry" "rig:TwistFollowElbow_L.ry"
		;
connectAttr "rig:TwistFollowElbow_L_parentConstraint1.crz" "rig:TwistFollowElbow_L.rz"
		;
connectAttr "rig:TwistFollowElbow_L.ro" "rig:TwistFollowElbow_L_parentConstraint1.cro"
		;
connectAttr "rig:TwistFollowElbow_L.pim" "rig:TwistFollowElbow_L_parentConstraint1.cpim"
		;
connectAttr "rig:TwistFollowElbow_L.rp" "rig:TwistFollowElbow_L_parentConstraint1.crp"
		;
connectAttr "rig:TwistFollowElbow_L.rpt" "rig:TwistFollowElbow_L_parentConstraint1.crt"
		;
connectAttr "rig:FKXElbow_L.t" "rig:TwistFollowElbow_L_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXElbow_L.rp" "rig:TwistFollowElbow_L_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXElbow_L.rpt" "rig:TwistFollowElbow_L_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXElbow_L.r" "rig:TwistFollowElbow_L_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXElbow_L.ro" "rig:TwistFollowElbow_L_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXElbow_L.s" "rig:TwistFollowElbow_L_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXElbow_L.pm" "rig:TwistFollowElbow_L_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXElbow_L.jo" "rig:TwistFollowElbow_L_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistFollowElbow_L_parentConstraint1.w0" "rig:TwistFollowElbow_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendArmReverse_L.ox" "rig:TwistFollowElbow_L_parentConstraint1.w0"
		;
connectAttr "rig:UnTwistElbow_L.msg" "rig:UnTwistIKElbow_L.hsj";
connectAttr "rig:effector11.hp" "rig:UnTwistIKElbow_L.hee";
connectAttr "rig:ikRPsolver.msg" "rig:UnTwistIKElbow_L.hsv";
connectAttr "rig:UnTwistIKElbow_L_poleVectorConstraint1.ctx" "rig:UnTwistIKElbow_L.pvx"
		;
connectAttr "rig:UnTwistIKElbow_L_poleVectorConstraint1.cty" "rig:UnTwistIKElbow_L.pvy"
		;
connectAttr "rig:UnTwistIKElbow_L_poleVectorConstraint1.ctz" "rig:UnTwistIKElbow_L.pvz"
		;
connectAttr "rig:UnTwistIKElbow_L.pim" "rig:UnTwistIKElbow_L_poleVectorConstraint1.cpim"
		;
connectAttr "rig:UnTwistElbow_L.pm" "rig:UnTwistIKElbow_L_poleVectorConstraint1.ps"
		;
connectAttr "rig:UnTwistElbow_L.t" "rig:UnTwistIKElbow_L_poleVectorConstraint1.crp"
		;
connectAttr "rig:UnTwistElbow_L.t" "rig:UnTwistIKElbow_L_poleVectorConstraint1.tg[0].tt"
		;
connectAttr "rig:UnTwistElbow_L.rp" "rig:UnTwistIKElbow_L_poleVectorConstraint1.tg[0].trp"
		;
connectAttr "rig:UnTwistElbow_L.rpt" "rig:UnTwistIKElbow_L_poleVectorConstraint1.tg[0].trt"
		;
connectAttr "rig:UnTwistElbow_L.pm" "rig:UnTwistIKElbow_L_poleVectorConstraint1.tg[0].tpm"
		;
connectAttr "rig:UnTwistIKElbow_L_poleVectorConstraint1.w0" "rig:UnTwistIKElbow_L_poleVectorConstraint1.tg[0].tw"
		;
connectAttr "rig:TwistFollowParentElbow_L_parentConstraint1.ctx" "rig:TwistFollowParentElbow_L.tx"
		;
connectAttr "rig:TwistFollowParentElbow_L_parentConstraint1.cty" "rig:TwistFollowParentElbow_L.ty"
		;
connectAttr "rig:TwistFollowParentElbow_L_parentConstraint1.ctz" "rig:TwistFollowParentElbow_L.tz"
		;
connectAttr "rig:TwistFollowParentElbow_L_parentConstraint1.crx" "rig:TwistFollowParentElbow_L.rx"
		;
connectAttr "rig:TwistFollowParentElbow_L_parentConstraint1.cry" "rig:TwistFollowParentElbow_L.ry"
		;
connectAttr "rig:TwistFollowParentElbow_L_parentConstraint1.crz" "rig:TwistFollowParentElbow_L.rz"
		;
connectAttr "rig:TwistFollowParentElbow_L.ro" "rig:TwistFollowParentElbow_L_parentConstraint1.cro"
		;
connectAttr "rig:TwistFollowParentElbow_L.pim" "rig:TwistFollowParentElbow_L_parentConstraint1.cpim"
		;
connectAttr "rig:TwistFollowParentElbow_L.rp" "rig:TwistFollowParentElbow_L_parentConstraint1.crp"
		;
connectAttr "rig:TwistFollowParentElbow_L.rpt" "rig:TwistFollowParentElbow_L_parentConstraint1.crt"
		;
connectAttr "rig:FKXShoulder_L.t" "rig:TwistFollowParentElbow_L_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXShoulder_L.rp" "rig:TwistFollowParentElbow_L_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXShoulder_L.rpt" "rig:TwistFollowParentElbow_L_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXShoulder_L.r" "rig:TwistFollowParentElbow_L_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXShoulder_L.ro" "rig:TwistFollowParentElbow_L_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXShoulder_L.s" "rig:TwistFollowParentElbow_L_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXShoulder_L.pm" "rig:TwistFollowParentElbow_L_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXShoulder_L.jo" "rig:TwistFollowParentElbow_L_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistFollowParentElbow_L_parentConstraint1.w0" "rig:TwistFollowParentElbow_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendArmReverse_L.ox" "rig:TwistFollowParentElbow_L_parentConstraint1.w0"
		;
connectAttr "rig:UnTwistElbow_L_pointConstraint1.ctx" "rig:UnTwistElbow_L.tx";
connectAttr "rig:UnTwistElbow_L_pointConstraint1.cty" "rig:UnTwistElbow_L.ty";
connectAttr "rig:UnTwistElbow_L_pointConstraint1.ctz" "rig:UnTwistElbow_L.tz";
connectAttr "rig:UnTwistElbow_L.s" "rig:UnTwistEndElbow_L.is";
connectAttr "rig:UnTwistElbow_L.pim" "rig:UnTwistElbow_L_pointConstraint1.cpim";
connectAttr "rig:UnTwistElbow_L.rp" "rig:UnTwistElbow_L_pointConstraint1.crp";
connectAttr "rig:UnTwistElbow_L.rpt" "rig:UnTwistElbow_L_pointConstraint1.crt";
connectAttr "rig:FKXElbow_L.t" "rig:UnTwistElbow_L_pointConstraint1.tg[0].tt";
connectAttr "rig:FKXElbow_L.rp" "rig:UnTwistElbow_L_pointConstraint1.tg[0].trp";
connectAttr "rig:FKXElbow_L.rpt" "rig:UnTwistElbow_L_pointConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXElbow_L.pm" "rig:UnTwistElbow_L_pointConstraint1.tg[0].tpm";
connectAttr "rig:UnTwistElbow_L_pointConstraint1.w0" "rig:UnTwistElbow_L_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendArmReverse_L.ox" "rig:UnTwistElbow_L_pointConstraint1.w0"
		;
connectAttr "rig:UnTwistEndElbow_L.tx" "rig:effector11.tx";
connectAttr "rig:UnTwistEndElbow_L.ty" "rig:effector11.ty";
connectAttr "rig:UnTwistEndElbow_L.tz" "rig:effector11.tz";
connectAttr "rig:UnTwistElbow_L.s" "rig:TwistBalancerElbow_L.is";
connectAttr "rig:TwistBalancerElbow_L_parentConstraint1.ctx" "rig:TwistBalancerElbow_L.tx"
		;
connectAttr "rig:TwistBalancerElbow_L_parentConstraint1.cty" "rig:TwistBalancerElbow_L.ty"
		;
connectAttr "rig:TwistBalancerElbow_L_parentConstraint1.ctz" "rig:TwistBalancerElbow_L.tz"
		;
connectAttr "rig:TwistBalancerElbow_L_parentConstraint1.crx" "rig:TwistBalancerElbow_L.rx"
		;
connectAttr "rig:TwistBalancerElbow_L_parentConstraint1.cry" "rig:TwistBalancerElbow_L.ry"
		;
connectAttr "rig:TwistBalancerElbow_L_parentConstraint1.crz" "rig:TwistBalancerElbow_L.rz"
		;
connectAttr "rig:TwistBalancerElbow_L.ro" "rig:TwistBalancerElbow_L_parentConstraint1.cro"
		;
connectAttr "rig:TwistBalancerElbow_L.pim" "rig:TwistBalancerElbow_L_parentConstraint1.cpim"
		;
connectAttr "rig:TwistBalancerElbow_L.rp" "rig:TwistBalancerElbow_L_parentConstraint1.crp"
		;
connectAttr "rig:TwistBalancerElbow_L.rpt" "rig:TwistBalancerElbow_L_parentConstraint1.crt"
		;
connectAttr "rig:TwistBalancerElbow_L.jo" "rig:TwistBalancerElbow_L_parentConstraint1.cjo"
		;
connectAttr "rig:FKXElbow_L.t" "rig:TwistBalancerElbow_L_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXElbow_L.rp" "rig:TwistBalancerElbow_L_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXElbow_L.rpt" "rig:TwistBalancerElbow_L_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXElbow_L.r" "rig:TwistBalancerElbow_L_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXElbow_L.ro" "rig:TwistBalancerElbow_L_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXElbow_L.s" "rig:TwistBalancerElbow_L_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXElbow_L.pm" "rig:TwistBalancerElbow_L_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXElbow_L.jo" "rig:TwistBalancerElbow_L_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistBalancerElbow_L_parentConstraint1.w0" "rig:TwistBalancerElbow_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendArmReverse_L.ox" "rig:TwistBalancerElbow_L_parentConstraint1.w0"
		;
connectAttr "rig:unitConversion79.o" "rig:TwisterElbow0_L.rx";
connectAttr "rig:unitConversion81.o" "rig:TwisterElbow1_L.rx";
connectAttr "rig:unitConversion83.o" "rig:TwisterElbow2_L.rx";
connectAttr "rig:TwistFollowShoulder_L_parentConstraint1.ctx" "rig:TwistFollowShoulder_L.tx"
		;
connectAttr "rig:TwistFollowShoulder_L_parentConstraint1.cty" "rig:TwistFollowShoulder_L.ty"
		;
connectAttr "rig:TwistFollowShoulder_L_parentConstraint1.ctz" "rig:TwistFollowShoulder_L.tz"
		;
connectAttr "rig:TwistFollowShoulder_L_parentConstraint1.crx" "rig:TwistFollowShoulder_L.rx"
		;
connectAttr "rig:TwistFollowShoulder_L_parentConstraint1.cry" "rig:TwistFollowShoulder_L.ry"
		;
connectAttr "rig:TwistFollowShoulder_L_parentConstraint1.crz" "rig:TwistFollowShoulder_L.rz"
		;
connectAttr "rig:TwistFollowShoulder_L.ro" "rig:TwistFollowShoulder_L_parentConstraint1.cro"
		;
connectAttr "rig:TwistFollowShoulder_L.pim" "rig:TwistFollowShoulder_L_parentConstraint1.cpim"
		;
connectAttr "rig:TwistFollowShoulder_L.rp" "rig:TwistFollowShoulder_L_parentConstraint1.crp"
		;
connectAttr "rig:TwistFollowShoulder_L.rpt" "rig:TwistFollowShoulder_L_parentConstraint1.crt"
		;
connectAttr "rig:FKXShoulder_L.t" "rig:TwistFollowShoulder_L_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXShoulder_L.rp" "rig:TwistFollowShoulder_L_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXShoulder_L.rpt" "rig:TwistFollowShoulder_L_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXShoulder_L.r" "rig:TwistFollowShoulder_L_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXShoulder_L.ro" "rig:TwistFollowShoulder_L_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXShoulder_L.s" "rig:TwistFollowShoulder_L_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXShoulder_L.pm" "rig:TwistFollowShoulder_L_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXShoulder_L.jo" "rig:TwistFollowShoulder_L_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistFollowShoulder_L_parentConstraint1.w0" "rig:TwistFollowShoulder_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendArmReverse_L.ox" "rig:TwistFollowShoulder_L_parentConstraint1.w0"
		;
connectAttr "rig:UnTwistShoulder_L.msg" "rig:UnTwistIKShoulder_L.hsj";
connectAttr "rig:effector12.hp" "rig:UnTwistIKShoulder_L.hee";
connectAttr "rig:ikRPsolver.msg" "rig:UnTwistIKShoulder_L.hsv";
connectAttr "rig:UnTwistIKShoulder_L_poleVectorConstraint1.ctx" "rig:UnTwistIKShoulder_L.pvx"
		;
connectAttr "rig:UnTwistIKShoulder_L_poleVectorConstraint1.cty" "rig:UnTwistIKShoulder_L.pvy"
		;
connectAttr "rig:UnTwistIKShoulder_L_poleVectorConstraint1.ctz" "rig:UnTwistIKShoulder_L.pvz"
		;
connectAttr "rig:UnTwistIKShoulder_L.pim" "rig:UnTwistIKShoulder_L_poleVectorConstraint1.cpim"
		;
connectAttr "rig:UnTwistShoulder_L.pm" "rig:UnTwistIKShoulder_L_poleVectorConstraint1.ps"
		;
connectAttr "rig:UnTwistShoulder_L.t" "rig:UnTwistIKShoulder_L_poleVectorConstraint1.crp"
		;
connectAttr "rig:UnTwistShoulder_L.t" "rig:UnTwistIKShoulder_L_poleVectorConstraint1.tg[0].tt"
		;
connectAttr "rig:UnTwistShoulder_L.rp" "rig:UnTwistIKShoulder_L_poleVectorConstraint1.tg[0].trp"
		;
connectAttr "rig:UnTwistShoulder_L.rpt" "rig:UnTwistIKShoulder_L_poleVectorConstraint1.tg[0].trt"
		;
connectAttr "rig:UnTwistShoulder_L.pm" "rig:UnTwistIKShoulder_L_poleVectorConstraint1.tg[0].tpm"
		;
connectAttr "rig:UnTwistIKShoulder_L_poleVectorConstraint1.w0" "rig:UnTwistIKShoulder_L_poleVectorConstraint1.tg[0].tw"
		;
connectAttr "rig:TwistFollowParentShoulder_L_parentConstraint1.ctx" "rig:TwistFollowParentShoulder_L.tx"
		;
connectAttr "rig:TwistFollowParentShoulder_L_parentConstraint1.cty" "rig:TwistFollowParentShoulder_L.ty"
		;
connectAttr "rig:TwistFollowParentShoulder_L_parentConstraint1.ctz" "rig:TwistFollowParentShoulder_L.tz"
		;
connectAttr "rig:TwistFollowParentShoulder_L_parentConstraint1.crx" "rig:TwistFollowParentShoulder_L.rx"
		;
connectAttr "rig:TwistFollowParentShoulder_L_parentConstraint1.cry" "rig:TwistFollowParentShoulder_L.ry"
		;
connectAttr "rig:TwistFollowParentShoulder_L_parentConstraint1.crz" "rig:TwistFollowParentShoulder_L.rz"
		;
connectAttr "rig:TwistFollowParentShoulder_L.ro" "rig:TwistFollowParentShoulder_L_parentConstraint1.cro"
		;
connectAttr "rig:TwistFollowParentShoulder_L.pim" "rig:TwistFollowParentShoulder_L_parentConstraint1.cpim"
		;
connectAttr "rig:TwistFollowParentShoulder_L.rp" "rig:TwistFollowParentShoulder_L_parentConstraint1.crp"
		;
connectAttr "rig:TwistFollowParentShoulder_L.rpt" "rig:TwistFollowParentShoulder_L_parentConstraint1.crt"
		;
connectAttr "rig:FKXScapula_L.t" "rig:TwistFollowParentShoulder_L_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXScapula_L.rp" "rig:TwistFollowParentShoulder_L_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXScapula_L.rpt" "rig:TwistFollowParentShoulder_L_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXScapula_L.r" "rig:TwistFollowParentShoulder_L_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXScapula_L.ro" "rig:TwistFollowParentShoulder_L_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXScapula_L.s" "rig:TwistFollowParentShoulder_L_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXScapula_L.pm" "rig:TwistFollowParentShoulder_L_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXScapula_L.jo" "rig:TwistFollowParentShoulder_L_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistFollowParentShoulder_L_parentConstraint1.w0" "rig:TwistFollowParentShoulder_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:UnTwistShoulder_L_pointConstraint1.ctx" "rig:UnTwistShoulder_L.tx"
		;
connectAttr "rig:UnTwistShoulder_L_pointConstraint1.cty" "rig:UnTwistShoulder_L.ty"
		;
connectAttr "rig:UnTwistShoulder_L_pointConstraint1.ctz" "rig:UnTwistShoulder_L.tz"
		;
connectAttr "rig:UnTwistShoulder_L.s" "rig:UnTwistEndShoulder_L.is";
connectAttr "rig:UnTwistShoulder_L.pim" "rig:UnTwistShoulder_L_pointConstraint1.cpim"
		;
connectAttr "rig:UnTwistShoulder_L.rp" "rig:UnTwistShoulder_L_pointConstraint1.crp"
		;
connectAttr "rig:UnTwistShoulder_L.rpt" "rig:UnTwistShoulder_L_pointConstraint1.crt"
		;
connectAttr "rig:FKXShoulder_L.t" "rig:UnTwistShoulder_L_pointConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXShoulder_L.rp" "rig:UnTwistShoulder_L_pointConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXShoulder_L.rpt" "rig:UnTwistShoulder_L_pointConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXShoulder_L.pm" "rig:UnTwistShoulder_L_pointConstraint1.tg[0].tpm"
		;
connectAttr "rig:UnTwistShoulder_L_pointConstraint1.w0" "rig:UnTwistShoulder_L_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendArmReverse_L.ox" "rig:UnTwistShoulder_L_pointConstraint1.w0"
		;
connectAttr "rig:UnTwistEndShoulder_L.tx" "rig:effector12.tx";
connectAttr "rig:UnTwistEndShoulder_L.ty" "rig:effector12.ty";
connectAttr "rig:UnTwistEndShoulder_L.tz" "rig:effector12.tz";
connectAttr "rig:UnTwistShoulder_L.s" "rig:TwistBalancerShoulder_L.is";
connectAttr "rig:TwistBalancerShoulder_L_parentConstraint1.ctx" "rig:TwistBalancerShoulder_L.tx"
		;
connectAttr "rig:TwistBalancerShoulder_L_parentConstraint1.cty" "rig:TwistBalancerShoulder_L.ty"
		;
connectAttr "rig:TwistBalancerShoulder_L_parentConstraint1.ctz" "rig:TwistBalancerShoulder_L.tz"
		;
connectAttr "rig:TwistBalancerShoulder_L_parentConstraint1.crx" "rig:TwistBalancerShoulder_L.rx"
		;
connectAttr "rig:TwistBalancerShoulder_L_parentConstraint1.cry" "rig:TwistBalancerShoulder_L.ry"
		;
connectAttr "rig:TwistBalancerShoulder_L_parentConstraint1.crz" "rig:TwistBalancerShoulder_L.rz"
		;
connectAttr "rig:TwistBalancerShoulder_L.ro" "rig:TwistBalancerShoulder_L_parentConstraint1.cro"
		;
connectAttr "rig:TwistBalancerShoulder_L.pim" "rig:TwistBalancerShoulder_L_parentConstraint1.cpim"
		;
connectAttr "rig:TwistBalancerShoulder_L.rp" "rig:TwistBalancerShoulder_L_parentConstraint1.crp"
		;
connectAttr "rig:TwistBalancerShoulder_L.rpt" "rig:TwistBalancerShoulder_L_parentConstraint1.crt"
		;
connectAttr "rig:TwistBalancerShoulder_L.jo" "rig:TwistBalancerShoulder_L_parentConstraint1.cjo"
		;
connectAttr "rig:FKXShoulder_L.t" "rig:TwistBalancerShoulder_L_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXShoulder_L.rp" "rig:TwistBalancerShoulder_L_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXShoulder_L.rpt" "rig:TwistBalancerShoulder_L_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXShoulder_L.r" "rig:TwistBalancerShoulder_L_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXShoulder_L.ro" "rig:TwistBalancerShoulder_L_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXShoulder_L.s" "rig:TwistBalancerShoulder_L_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXShoulder_L.pm" "rig:TwistBalancerShoulder_L_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXShoulder_L.jo" "rig:TwistBalancerShoulder_L_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:TwistBalancerShoulder_L_parentConstraint1.w0" "rig:TwistBalancerShoulder_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendArmReverse_L.ox" "rig:TwistBalancerShoulder_L_parentConstraint1.w0"
		;
connectAttr "rig:unitConversion85.o" "rig:TwisterShoulder0_L.rx";
connectAttr "rig:unitConversion87.o" "rig:TwisterShoulder1_L.rx";
connectAttr "rig:unitConversion89.o" "rig:TwisterShoulder2_L.rx";
connectAttr "rig:FKIKMixKnee_R_pointConstraint1.ctx" "rig:FKIKMixKnee_R.tx";
connectAttr "rig:FKIKMixKnee_R_pointConstraint1.cty" "rig:FKIKMixKnee_R.ty";
connectAttr "rig:FKIKMixKnee_R_pointConstraint1.ctz" "rig:FKIKMixKnee_R.tz";
connectAttr "rig:FKIKMixKnee_R.pim" "rig:FKIKMixKnee_R_pointConstraint1.cpim";
connectAttr "rig:FKIKMixKnee_R.rp" "rig:FKIKMixKnee_R_pointConstraint1.crp";
connectAttr "rig:FKIKMixKnee_R.rpt" "rig:FKIKMixKnee_R_pointConstraint1.crt";
connectAttr "rig:FKXKnee_R.t" "rig:FKIKMixKnee_R_pointConstraint1.tg[0].tt";
connectAttr "rig:FKXKnee_R.rp" "rig:FKIKMixKnee_R_pointConstraint1.tg[0].trp";
connectAttr "rig:FKXKnee_R.rpt" "rig:FKIKMixKnee_R_pointConstraint1.tg[0].trt";
connectAttr "rig:FKXKnee_R.pm" "rig:FKIKMixKnee_R_pointConstraint1.tg[0].tpm";
connectAttr "rig:FKIKMixKnee_R_pointConstraint1.w0" "rig:FKIKMixKnee_R_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKMixKnee_L_pointConstraint1.ctx" "rig:FKIKMixKnee_L.tx";
connectAttr "rig:FKIKMixKnee_L_pointConstraint1.cty" "rig:FKIKMixKnee_L.ty";
connectAttr "rig:FKIKMixKnee_L_pointConstraint1.ctz" "rig:FKIKMixKnee_L.tz";
connectAttr "rig:FKIKMixKnee_L.pim" "rig:FKIKMixKnee_L_pointConstraint1.cpim";
connectAttr "rig:FKIKMixKnee_L.rp" "rig:FKIKMixKnee_L_pointConstraint1.crp";
connectAttr "rig:FKIKMixKnee_L.rpt" "rig:FKIKMixKnee_L_pointConstraint1.crt";
connectAttr "rig:FKXKnee_L.t" "rig:FKIKMixKnee_L_pointConstraint1.tg[0].tt";
connectAttr "rig:FKXKnee_L.rp" "rig:FKIKMixKnee_L_pointConstraint1.tg[0].trp";
connectAttr "rig:FKXKnee_L.rpt" "rig:FKIKMixKnee_L_pointConstraint1.tg[0].trt";
connectAttr "rig:FKXKnee_L.pm" "rig:FKIKMixKnee_L_pointConstraint1.tg[0].tpm";
connectAttr "rig:FKIKMixKnee_L_pointConstraint1.w0" "rig:FKIKMixKnee_L_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKMixWrist_L_pointConstraint1.ctx" "rig:FKIKMixWrist_L.tx";
connectAttr "rig:FKIKMixWrist_L_pointConstraint1.cty" "rig:FKIKMixWrist_L.ty";
connectAttr "rig:FKIKMixWrist_L_pointConstraint1.ctz" "rig:FKIKMixWrist_L.tz";
connectAttr "rig:FKIKMixWrist_L.pim" "rig:FKIKMixWrist_L_pointConstraint1.cpim";
connectAttr "rig:FKIKMixWrist_L.rp" "rig:FKIKMixWrist_L_pointConstraint1.crp";
connectAttr "rig:FKIKMixWrist_L.rpt" "rig:FKIKMixWrist_L_pointConstraint1.crt";
connectAttr "rig:FKXWrist_L.t" "rig:FKIKMixWrist_L_pointConstraint1.tg[0].tt";
connectAttr "rig:FKXWrist_L.rp" "rig:FKIKMixWrist_L_pointConstraint1.tg[0].trp";
connectAttr "rig:FKXWrist_L.rpt" "rig:FKIKMixWrist_L_pointConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXWrist_L.pm" "rig:FKIKMixWrist_L_pointConstraint1.tg[0].tpm";
connectAttr "rig:FKIKMixWrist_L_pointConstraint1.w0" "rig:FKIKMixWrist_L_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendArmReverse_L.ox" "rig:FKIKMixWrist_L_pointConstraint1.w0"
		;
connectAttr "rig:FKIKMixElbow_L_pointConstraint1.ctx" "rig:FKIKMixElbow_L.tx";
connectAttr "rig:FKIKMixElbow_L_pointConstraint1.cty" "rig:FKIKMixElbow_L.ty";
connectAttr "rig:FKIKMixElbow_L_pointConstraint1.ctz" "rig:FKIKMixElbow_L.tz";
connectAttr "rig:FKIKMixElbow_L.pim" "rig:FKIKMixElbow_L_pointConstraint1.cpim";
connectAttr "rig:FKIKMixElbow_L.rp" "rig:FKIKMixElbow_L_pointConstraint1.crp";
connectAttr "rig:FKIKMixElbow_L.rpt" "rig:FKIKMixElbow_L_pointConstraint1.crt";
connectAttr "rig:FKXElbow_L.t" "rig:FKIKMixElbow_L_pointConstraint1.tg[0].tt";
connectAttr "rig:FKXElbow_L.rp" "rig:FKIKMixElbow_L_pointConstraint1.tg[0].trp";
connectAttr "rig:FKXElbow_L.rpt" "rig:FKIKMixElbow_L_pointConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXElbow_L.pm" "rig:FKIKMixElbow_L_pointConstraint1.tg[0].tpm";
connectAttr "rig:FKIKMixElbow_L_pointConstraint1.w0" "rig:FKIKMixElbow_L_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendArmReverse_L.ox" "rig:FKIKMixElbow_L_pointConstraint1.w0"
		;
connectAttr "rig:Ankle_R.ro" "rig:Ankle_R_parentConstraint1.cro";
connectAttr "rig:Ankle_R.pim" "rig:Ankle_R_parentConstraint1.cpim";
connectAttr "rig:Ankle_R.rp" "rig:Ankle_R_parentConstraint1.crp";
connectAttr "rig:Ankle_R.rpt" "rig:Ankle_R_parentConstraint1.crt";
connectAttr "rig:Ankle_R.jo" "rig:Ankle_R_parentConstraint1.cjo";
connectAttr "rig:FKXAnkle_R.t" "rig:Ankle_R_parentConstraint1.tg[0].tt";
connectAttr "rig:FKXAnkle_R.rp" "rig:Ankle_R_parentConstraint1.tg[0].trp";
connectAttr "rig:FKXAnkle_R.rpt" "rig:Ankle_R_parentConstraint1.tg[0].trt";
connectAttr "rig:FKXAnkle_R.r" "rig:Ankle_R_parentConstraint1.tg[0].tr";
connectAttr "rig:FKXAnkle_R.ro" "rig:Ankle_R_parentConstraint1.tg[0].tro";
connectAttr "rig:FKXAnkle_R.s" "rig:Ankle_R_parentConstraint1.tg[0].ts";
connectAttr "rig:FKXAnkle_R.pm" "rig:Ankle_R_parentConstraint1.tg[0].tpm";
connectAttr "rig:FKXAnkle_R.jo" "rig:Ankle_R_parentConstraint1.tg[0].tjo";
connectAttr "rig:Ankle_R_parentConstraint1.w0" "rig:Ankle_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:Knee_R.ro" "rig:Knee_R_parentConstraint1.cro";
connectAttr "rig:Knee_R.pim" "rig:Knee_R_parentConstraint1.cpim";
connectAttr "rig:Knee_R.rp" "rig:Knee_R_parentConstraint1.crp";
connectAttr "rig:Knee_R.rpt" "rig:Knee_R_parentConstraint1.crt";
connectAttr "rig:Knee_R.jo" "rig:Knee_R_parentConstraint1.cjo";
connectAttr "rig:FKXKnee_R.t" "rig:Knee_R_parentConstraint1.tg[0].tt";
connectAttr "rig:FKXKnee_R.rp" "rig:Knee_R_parentConstraint1.tg[0].trp";
connectAttr "rig:FKXKnee_R.rpt" "rig:Knee_R_parentConstraint1.tg[0].trt";
connectAttr "rig:FKXKnee_R.r" "rig:Knee_R_parentConstraint1.tg[0].tr";
connectAttr "rig:FKXKnee_R.ro" "rig:Knee_R_parentConstraint1.tg[0].tro";
connectAttr "rig:FKXKnee_R.s" "rig:Knee_R_parentConstraint1.tg[0].ts";
connectAttr "rig:FKXKnee_R.pm" "rig:Knee_R_parentConstraint1.tg[0].tpm";
connectAttr "rig:FKXKnee_R.jo" "rig:Knee_R_parentConstraint1.tg[0].tjo";
connectAttr "rig:Knee_R_parentConstraint1.w0" "rig:Knee_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:IndexFinger3_R.ro" "rig:IndexFinger3_R_parentConstraint1.cro";
connectAttr "rig:IndexFinger3_R.pim" "rig:IndexFinger3_R_parentConstraint1.cpim"
		;
connectAttr "rig:IndexFinger3_R.rp" "rig:IndexFinger3_R_parentConstraint1.crp";
connectAttr "rig:IndexFinger3_R.rpt" "rig:IndexFinger3_R_parentConstraint1.crt";
connectAttr "rig:IndexFinger3_R.jo" "rig:IndexFinger3_R_parentConstraint1.cjo";
connectAttr "rig:FKXIndexFinger3_R.t" "rig:IndexFinger3_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXIndexFinger3_R.rp" "rig:IndexFinger3_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXIndexFinger3_R.rpt" "rig:IndexFinger3_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXIndexFinger3_R.r" "rig:IndexFinger3_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXIndexFinger3_R.ro" "rig:IndexFinger3_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXIndexFinger3_R.s" "rig:IndexFinger3_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXIndexFinger3_R.pm" "rig:IndexFinger3_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXIndexFinger3_R.jo" "rig:IndexFinger3_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:IndexFinger3_R_parentConstraint1.w0" "rig:IndexFinger3_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:IndexFinger2_R.ro" "rig:IndexFinger2_R_parentConstraint1.cro";
connectAttr "rig:IndexFinger2_R.pim" "rig:IndexFinger2_R_parentConstraint1.cpim"
		;
connectAttr "rig:IndexFinger2_R.rp" "rig:IndexFinger2_R_parentConstraint1.crp";
connectAttr "rig:IndexFinger2_R.rpt" "rig:IndexFinger2_R_parentConstraint1.crt";
connectAttr "rig:IndexFinger2_R.jo" "rig:IndexFinger2_R_parentConstraint1.cjo";
connectAttr "rig:FKXIndexFinger2_R.t" "rig:IndexFinger2_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXIndexFinger2_R.rp" "rig:IndexFinger2_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXIndexFinger2_R.rpt" "rig:IndexFinger2_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXIndexFinger2_R.r" "rig:IndexFinger2_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXIndexFinger2_R.ro" "rig:IndexFinger2_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXIndexFinger2_R.s" "rig:IndexFinger2_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXIndexFinger2_R.pm" "rig:IndexFinger2_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXIndexFinger2_R.jo" "rig:IndexFinger2_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:IndexFinger2_R_parentConstraint1.w0" "rig:IndexFinger2_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:IndexFinger1_R.ro" "rig:IndexFinger1_R_parentConstraint1.cro";
connectAttr "rig:IndexFinger1_R.pim" "rig:IndexFinger1_R_parentConstraint1.cpim"
		;
connectAttr "rig:IndexFinger1_R.rp" "rig:IndexFinger1_R_parentConstraint1.crp";
connectAttr "rig:IndexFinger1_R.rpt" "rig:IndexFinger1_R_parentConstraint1.crt";
connectAttr "rig:IndexFinger1_R.jo" "rig:IndexFinger1_R_parentConstraint1.cjo";
connectAttr "rig:FKXIndexFinger1_R.t" "rig:IndexFinger1_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXIndexFinger1_R.rp" "rig:IndexFinger1_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXIndexFinger1_R.rpt" "rig:IndexFinger1_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXIndexFinger1_R.r" "rig:IndexFinger1_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXIndexFinger1_R.ro" "rig:IndexFinger1_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXIndexFinger1_R.s" "rig:IndexFinger1_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXIndexFinger1_R.pm" "rig:IndexFinger1_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXIndexFinger1_R.jo" "rig:IndexFinger1_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:IndexFinger1_R_parentConstraint1.w0" "rig:IndexFinger1_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:MiddleFinger3_R.ro" "rig:MiddleFinger3_R_parentConstraint1.cro"
		;
connectAttr "rig:MiddleFinger3_R.pim" "rig:MiddleFinger3_R_parentConstraint1.cpim"
		;
connectAttr "rig:MiddleFinger3_R.rp" "rig:MiddleFinger3_R_parentConstraint1.crp"
		;
connectAttr "rig:MiddleFinger3_R.rpt" "rig:MiddleFinger3_R_parentConstraint1.crt"
		;
connectAttr "rig:MiddleFinger3_R.jo" "rig:MiddleFinger3_R_parentConstraint1.cjo"
		;
connectAttr "rig:FKXMiddleFinger3_R.t" "rig:MiddleFinger3_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXMiddleFinger3_R.rp" "rig:MiddleFinger3_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXMiddleFinger3_R.rpt" "rig:MiddleFinger3_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXMiddleFinger3_R.r" "rig:MiddleFinger3_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXMiddleFinger3_R.ro" "rig:MiddleFinger3_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXMiddleFinger3_R.s" "rig:MiddleFinger3_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXMiddleFinger3_R.pm" "rig:MiddleFinger3_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXMiddleFinger3_R.jo" "rig:MiddleFinger3_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:MiddleFinger3_R_parentConstraint1.w0" "rig:MiddleFinger3_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:MiddleFinger2_R.ro" "rig:MiddleFinger2_R_parentConstraint1.cro"
		;
connectAttr "rig:MiddleFinger2_R.pim" "rig:MiddleFinger2_R_parentConstraint1.cpim"
		;
connectAttr "rig:MiddleFinger2_R.rp" "rig:MiddleFinger2_R_parentConstraint1.crp"
		;
connectAttr "rig:MiddleFinger2_R.rpt" "rig:MiddleFinger2_R_parentConstraint1.crt"
		;
connectAttr "rig:MiddleFinger2_R.jo" "rig:MiddleFinger2_R_parentConstraint1.cjo"
		;
connectAttr "rig:FKXMiddleFinger2_R.t" "rig:MiddleFinger2_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXMiddleFinger2_R.rp" "rig:MiddleFinger2_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXMiddleFinger2_R.rpt" "rig:MiddleFinger2_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXMiddleFinger2_R.r" "rig:MiddleFinger2_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXMiddleFinger2_R.ro" "rig:MiddleFinger2_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXMiddleFinger2_R.s" "rig:MiddleFinger2_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXMiddleFinger2_R.pm" "rig:MiddleFinger2_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXMiddleFinger2_R.jo" "rig:MiddleFinger2_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:MiddleFinger2_R_parentConstraint1.w0" "rig:MiddleFinger2_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:MiddleFinger1_R.ro" "rig:MiddleFinger1_R_parentConstraint1.cro"
		;
connectAttr "rig:MiddleFinger1_R.pim" "rig:MiddleFinger1_R_parentConstraint1.cpim"
		;
connectAttr "rig:MiddleFinger1_R.rp" "rig:MiddleFinger1_R_parentConstraint1.crp"
		;
connectAttr "rig:MiddleFinger1_R.rpt" "rig:MiddleFinger1_R_parentConstraint1.crt"
		;
connectAttr "rig:MiddleFinger1_R.jo" "rig:MiddleFinger1_R_parentConstraint1.cjo"
		;
connectAttr "rig:FKXMiddleFinger1_R.t" "rig:MiddleFinger1_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXMiddleFinger1_R.rp" "rig:MiddleFinger1_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXMiddleFinger1_R.rpt" "rig:MiddleFinger1_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXMiddleFinger1_R.r" "rig:MiddleFinger1_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXMiddleFinger1_R.ro" "rig:MiddleFinger1_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXMiddleFinger1_R.s" "rig:MiddleFinger1_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXMiddleFinger1_R.pm" "rig:MiddleFinger1_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXMiddleFinger1_R.jo" "rig:MiddleFinger1_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:MiddleFinger1_R_parentConstraint1.w0" "rig:MiddleFinger1_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:PinkyFinger3_R.ro" "rig:PinkyFinger3_R_parentConstraint1.cro";
connectAttr "rig:PinkyFinger3_R.pim" "rig:PinkyFinger3_R_parentConstraint1.cpim"
		;
connectAttr "rig:PinkyFinger3_R.rp" "rig:PinkyFinger3_R_parentConstraint1.crp";
connectAttr "rig:PinkyFinger3_R.rpt" "rig:PinkyFinger3_R_parentConstraint1.crt";
connectAttr "rig:PinkyFinger3_R.jo" "rig:PinkyFinger3_R_parentConstraint1.cjo";
connectAttr "rig:FKXPinkyFinger3_R.t" "rig:PinkyFinger3_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXPinkyFinger3_R.rp" "rig:PinkyFinger3_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXPinkyFinger3_R.rpt" "rig:PinkyFinger3_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXPinkyFinger3_R.r" "rig:PinkyFinger3_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXPinkyFinger3_R.ro" "rig:PinkyFinger3_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXPinkyFinger3_R.s" "rig:PinkyFinger3_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXPinkyFinger3_R.pm" "rig:PinkyFinger3_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXPinkyFinger3_R.jo" "rig:PinkyFinger3_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:PinkyFinger3_R_parentConstraint1.w0" "rig:PinkyFinger3_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:PinkyFinger2_R.ro" "rig:PinkyFinger2_R_parentConstraint1.cro";
connectAttr "rig:PinkyFinger2_R.pim" "rig:PinkyFinger2_R_parentConstraint1.cpim"
		;
connectAttr "rig:PinkyFinger2_R.rp" "rig:PinkyFinger2_R_parentConstraint1.crp";
connectAttr "rig:PinkyFinger2_R.rpt" "rig:PinkyFinger2_R_parentConstraint1.crt";
connectAttr "rig:PinkyFinger2_R.jo" "rig:PinkyFinger2_R_parentConstraint1.cjo";
connectAttr "rig:FKXPinkyFinger2_R.t" "rig:PinkyFinger2_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXPinkyFinger2_R.rp" "rig:PinkyFinger2_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXPinkyFinger2_R.rpt" "rig:PinkyFinger2_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXPinkyFinger2_R.r" "rig:PinkyFinger2_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXPinkyFinger2_R.ro" "rig:PinkyFinger2_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXPinkyFinger2_R.s" "rig:PinkyFinger2_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXPinkyFinger2_R.pm" "rig:PinkyFinger2_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXPinkyFinger2_R.jo" "rig:PinkyFinger2_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:PinkyFinger2_R_parentConstraint1.w0" "rig:PinkyFinger2_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:PinkyFinger1_R.ro" "rig:PinkyFinger1_R_parentConstraint1.cro";
connectAttr "rig:PinkyFinger1_R.pim" "rig:PinkyFinger1_R_parentConstraint1.cpim"
		;
connectAttr "rig:PinkyFinger1_R.rp" "rig:PinkyFinger1_R_parentConstraint1.crp";
connectAttr "rig:PinkyFinger1_R.rpt" "rig:PinkyFinger1_R_parentConstraint1.crt";
connectAttr "rig:PinkyFinger1_R.jo" "rig:PinkyFinger1_R_parentConstraint1.cjo";
connectAttr "rig:FKXPinkyFinger1_R.t" "rig:PinkyFinger1_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXPinkyFinger1_R.rp" "rig:PinkyFinger1_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXPinkyFinger1_R.rpt" "rig:PinkyFinger1_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXPinkyFinger1_R.r" "rig:PinkyFinger1_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXPinkyFinger1_R.ro" "rig:PinkyFinger1_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXPinkyFinger1_R.s" "rig:PinkyFinger1_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXPinkyFinger1_R.pm" "rig:PinkyFinger1_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXPinkyFinger1_R.jo" "rig:PinkyFinger1_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:PinkyFinger1_R_parentConstraint1.w0" "rig:PinkyFinger1_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:RingFinger3_R.ro" "rig:RingFinger3_R_parentConstraint1.cro";
connectAttr "rig:RingFinger3_R.pim" "rig:RingFinger3_R_parentConstraint1.cpim";
connectAttr "rig:RingFinger3_R.rp" "rig:RingFinger3_R_parentConstraint1.crp";
connectAttr "rig:RingFinger3_R.rpt" "rig:RingFinger3_R_parentConstraint1.crt";
connectAttr "rig:RingFinger3_R.jo" "rig:RingFinger3_R_parentConstraint1.cjo";
connectAttr "rig:FKXRingFinger3_R.t" "rig:RingFinger3_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXRingFinger3_R.rp" "rig:RingFinger3_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXRingFinger3_R.rpt" "rig:RingFinger3_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXRingFinger3_R.r" "rig:RingFinger3_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXRingFinger3_R.ro" "rig:RingFinger3_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXRingFinger3_R.s" "rig:RingFinger3_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXRingFinger3_R.pm" "rig:RingFinger3_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXRingFinger3_R.jo" "rig:RingFinger3_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:RingFinger3_R_parentConstraint1.w0" "rig:RingFinger3_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:RingFinger2_R.ro" "rig:RingFinger2_R_parentConstraint1.cro";
connectAttr "rig:RingFinger2_R.pim" "rig:RingFinger2_R_parentConstraint1.cpim";
connectAttr "rig:RingFinger2_R.rp" "rig:RingFinger2_R_parentConstraint1.crp";
connectAttr "rig:RingFinger2_R.rpt" "rig:RingFinger2_R_parentConstraint1.crt";
connectAttr "rig:RingFinger2_R.jo" "rig:RingFinger2_R_parentConstraint1.cjo";
connectAttr "rig:FKXRingFinger2_R.t" "rig:RingFinger2_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXRingFinger2_R.rp" "rig:RingFinger2_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXRingFinger2_R.rpt" "rig:RingFinger2_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXRingFinger2_R.r" "rig:RingFinger2_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXRingFinger2_R.ro" "rig:RingFinger2_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXRingFinger2_R.s" "rig:RingFinger2_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXRingFinger2_R.pm" "rig:RingFinger2_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXRingFinger2_R.jo" "rig:RingFinger2_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:RingFinger2_R_parentConstraint1.w0" "rig:RingFinger2_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:RingFinger1_R.ro" "rig:RingFinger1_R_parentConstraint1.cro";
connectAttr "rig:RingFinger1_R.pim" "rig:RingFinger1_R_parentConstraint1.cpim";
connectAttr "rig:RingFinger1_R.rp" "rig:RingFinger1_R_parentConstraint1.crp";
connectAttr "rig:RingFinger1_R.rpt" "rig:RingFinger1_R_parentConstraint1.crt";
connectAttr "rig:RingFinger1_R.jo" "rig:RingFinger1_R_parentConstraint1.cjo";
connectAttr "rig:FKXRingFinger1_R.t" "rig:RingFinger1_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXRingFinger1_R.rp" "rig:RingFinger1_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXRingFinger1_R.rpt" "rig:RingFinger1_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXRingFinger1_R.r" "rig:RingFinger1_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXRingFinger1_R.ro" "rig:RingFinger1_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXRingFinger1_R.s" "rig:RingFinger1_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXRingFinger1_R.pm" "rig:RingFinger1_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXRingFinger1_R.jo" "rig:RingFinger1_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:RingFinger1_R_parentConstraint1.w0" "rig:RingFinger1_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:Cup_R.ro" "rig:Cup_R_parentConstraint1.cro";
connectAttr "rig:Cup_R.pim" "rig:Cup_R_parentConstraint1.cpim";
connectAttr "rig:Cup_R.rp" "rig:Cup_R_parentConstraint1.crp";
connectAttr "rig:Cup_R.rpt" "rig:Cup_R_parentConstraint1.crt";
connectAttr "rig:Cup_R.jo" "rig:Cup_R_parentConstraint1.cjo";
connectAttr "rig:FKXCup_R.t" "rig:Cup_R_parentConstraint1.tg[0].tt";
connectAttr "rig:FKXCup_R.rp" "rig:Cup_R_parentConstraint1.tg[0].trp";
connectAttr "rig:FKXCup_R.rpt" "rig:Cup_R_parentConstraint1.tg[0].trt";
connectAttr "rig:FKXCup_R.r" "rig:Cup_R_parentConstraint1.tg[0].tr";
connectAttr "rig:FKXCup_R.ro" "rig:Cup_R_parentConstraint1.tg[0].tro";
connectAttr "rig:FKXCup_R.s" "rig:Cup_R_parentConstraint1.tg[0].ts";
connectAttr "rig:FKXCup_R.pm" "rig:Cup_R_parentConstraint1.tg[0].tpm";
connectAttr "rig:FKXCup_R.jo" "rig:Cup_R_parentConstraint1.tg[0].tjo";
connectAttr "rig:Cup_R_parentConstraint1.w0" "rig:Cup_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:ThumbFinger3_R.ro" "rig:ThumbFinger3_R_parentConstraint1.cro";
connectAttr "rig:ThumbFinger3_R.pim" "rig:ThumbFinger3_R_parentConstraint1.cpim"
		;
connectAttr "rig:ThumbFinger3_R.rp" "rig:ThumbFinger3_R_parentConstraint1.crp";
connectAttr "rig:ThumbFinger3_R.rpt" "rig:ThumbFinger3_R_parentConstraint1.crt";
connectAttr "rig:ThumbFinger3_R.jo" "rig:ThumbFinger3_R_parentConstraint1.cjo";
connectAttr "rig:FKXThumbFinger3_R.t" "rig:ThumbFinger3_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXThumbFinger3_R.rp" "rig:ThumbFinger3_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXThumbFinger3_R.rpt" "rig:ThumbFinger3_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXThumbFinger3_R.r" "rig:ThumbFinger3_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXThumbFinger3_R.ro" "rig:ThumbFinger3_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXThumbFinger3_R.s" "rig:ThumbFinger3_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXThumbFinger3_R.pm" "rig:ThumbFinger3_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXThumbFinger3_R.jo" "rig:ThumbFinger3_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:ThumbFinger3_R_parentConstraint1.w0" "rig:ThumbFinger3_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:ThumbFinger2_R.ro" "rig:ThumbFinger2_R_parentConstraint1.cro";
connectAttr "rig:ThumbFinger2_R.pim" "rig:ThumbFinger2_R_parentConstraint1.cpim"
		;
connectAttr "rig:ThumbFinger2_R.rp" "rig:ThumbFinger2_R_parentConstraint1.crp";
connectAttr "rig:ThumbFinger2_R.rpt" "rig:ThumbFinger2_R_parentConstraint1.crt";
connectAttr "rig:ThumbFinger2_R.jo" "rig:ThumbFinger2_R_parentConstraint1.cjo";
connectAttr "rig:FKXThumbFinger2_R.t" "rig:ThumbFinger2_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXThumbFinger2_R.rp" "rig:ThumbFinger2_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXThumbFinger2_R.rpt" "rig:ThumbFinger2_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXThumbFinger2_R.r" "rig:ThumbFinger2_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXThumbFinger2_R.ro" "rig:ThumbFinger2_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXThumbFinger2_R.s" "rig:ThumbFinger2_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXThumbFinger2_R.pm" "rig:ThumbFinger2_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXThumbFinger2_R.jo" "rig:ThumbFinger2_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:ThumbFinger2_R_parentConstraint1.w0" "rig:ThumbFinger2_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:ThumbFinger1_R.ro" "rig:ThumbFinger1_R_parentConstraint1.cro";
connectAttr "rig:ThumbFinger1_R.pim" "rig:ThumbFinger1_R_parentConstraint1.cpim"
		;
connectAttr "rig:ThumbFinger1_R.rp" "rig:ThumbFinger1_R_parentConstraint1.crp";
connectAttr "rig:ThumbFinger1_R.rpt" "rig:ThumbFinger1_R_parentConstraint1.crt";
connectAttr "rig:ThumbFinger1_R.jo" "rig:ThumbFinger1_R_parentConstraint1.cjo";
connectAttr "rig:FKXThumbFinger1_R.t" "rig:ThumbFinger1_R_parentConstraint1.tg[0].tt"
		;
connectAttr "rig:FKXThumbFinger1_R.rp" "rig:ThumbFinger1_R_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXThumbFinger1_R.rpt" "rig:ThumbFinger1_R_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXThumbFinger1_R.r" "rig:ThumbFinger1_R_parentConstraint1.tg[0].tr"
		;
connectAttr "rig:FKXThumbFinger1_R.ro" "rig:ThumbFinger1_R_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXThumbFinger1_R.s" "rig:ThumbFinger1_R_parentConstraint1.tg[0].ts"
		;
connectAttr "rig:FKXThumbFinger1_R.pm" "rig:ThumbFinger1_R_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXThumbFinger1_R.jo" "rig:ThumbFinger1_R_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:ThumbFinger1_R_parentConstraint1.w0" "rig:ThumbFinger1_R_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:NeckPart2_M.ro" "rig:NeckPart2_M_parentConstraint1.cro";
connectAttr "rig:NeckPart2_M.pim" "rig:NeckPart2_M_parentConstraint1.cpim";
connectAttr "rig:NeckPart2_M.rp" "rig:NeckPart2_M_parentConstraint1.crp";
connectAttr "rig:NeckPart2_M.rpt" "rig:NeckPart2_M_parentConstraint1.crt";
connectAttr "rig:NeckPart2_M.jo" "rig:NeckPart2_M_parentConstraint1.cjo";
connectAttr "rig:NeckPart2_M_parentConstraint1.w0" "rig:NeckPart2_M_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:unitConversion4.o" "rig:NeckPart2_M_parentConstraint1.tg[0].torx"
		;
connectAttr "rig:NeckPart1_M.ro" "rig:NeckPart1_M_parentConstraint1.cro";
connectAttr "rig:NeckPart1_M.pim" "rig:NeckPart1_M_parentConstraint1.cpim";
connectAttr "rig:NeckPart1_M.rp" "rig:NeckPart1_M_parentConstraint1.crp";
connectAttr "rig:NeckPart1_M.rpt" "rig:NeckPart1_M_parentConstraint1.crt";
connectAttr "rig:NeckPart1_M.jo" "rig:NeckPart1_M_parentConstraint1.cjo";
connectAttr "rig:NeckPart1_M_parentConstraint1.w0" "rig:NeckPart1_M_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:unitConversion2.o" "rig:NeckPart1_M_parentConstraint1.tg[0].torx"
		;
connectAttr "rig:Chest_M.ro" "rig:Chest_M_parentConstraint1.cro";
connectAttr "rig:Chest_M.pim" "rig:Chest_M_parentConstraint1.cpim";
connectAttr "rig:Chest_M.rp" "rig:Chest_M_parentConstraint1.crp";
connectAttr "rig:Chest_M.rpt" "rig:Chest_M_parentConstraint1.crt";
connectAttr "rig:Chest_M.jo" "rig:Chest_M_parentConstraint1.cjo";
connectAttr "rig:FKXChest_M.t" "rig:Chest_M_parentConstraint1.tg[0].tt";
connectAttr "rig:FKXChest_M.rp" "rig:Chest_M_parentConstraint1.tg[0].trp";
connectAttr "rig:FKXChest_M.rpt" "rig:Chest_M_parentConstraint1.tg[0].trt";
connectAttr "rig:FKXChest_M.r" "rig:Chest_M_parentConstraint1.tg[0].tr";
connectAttr "rig:FKXChest_M.ro" "rig:Chest_M_parentConstraint1.tg[0].tro";
connectAttr "rig:FKXChest_M.s" "rig:Chest_M_parentConstraint1.tg[0].ts";
connectAttr "rig:FKXChest_M.pm" "rig:Chest_M_parentConstraint1.tg[0].tpm";
connectAttr "rig:FKXChest_M.jo" "rig:Chest_M_parentConstraint1.tg[0].tjo";
connectAttr "rig:Chest_M_parentConstraint1.w0" "rig:Chest_M_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendSpineReverse_M.ox" "rig:Chest_M_parentConstraint1.w0";
connectAttr "rig:Spine2_M.ro" "rig:Spine2_M_parentConstraint1.cro";
connectAttr "rig:Spine2_M.pim" "rig:Spine2_M_parentConstraint1.cpim";
connectAttr "rig:Spine2_M.rp" "rig:Spine2_M_parentConstraint1.crp";
connectAttr "rig:Spine2_M.rpt" "rig:Spine2_M_parentConstraint1.crt";
connectAttr "rig:Spine2_M.jo" "rig:Spine2_M_parentConstraint1.cjo";
connectAttr "rig:FKXSpine2_M.t" "rig:Spine2_M_parentConstraint1.tg[0].tt";
connectAttr "rig:FKXSpine2_M.rp" "rig:Spine2_M_parentConstraint1.tg[0].trp";
connectAttr "rig:FKXSpine2_M.rpt" "rig:Spine2_M_parentConstraint1.tg[0].trt";
connectAttr "rig:FKXSpine2_M.r" "rig:Spine2_M_parentConstraint1.tg[0].tr";
connectAttr "rig:FKXSpine2_M.ro" "rig:Spine2_M_parentConstraint1.tg[0].tro";
connectAttr "rig:FKXSpine2_M.s" "rig:Spine2_M_parentConstraint1.tg[0].ts";
connectAttr "rig:FKXSpine2_M.pm" "rig:Spine2_M_parentConstraint1.tg[0].tpm";
connectAttr "rig:FKXSpine2_M.jo" "rig:Spine2_M_parentConstraint1.tg[0].tjo";
connectAttr "rig:Spine2_M_parentConstraint1.w0" "rig:Spine2_M_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendSpineReverse_M.ox" "rig:Spine2_M_parentConstraint1.w0"
		;
connectAttr "rig:Spine1_M.ro" "rig:Spine1_M_parentConstraint1.cro";
connectAttr "rig:Spine1_M.pim" "rig:Spine1_M_parentConstraint1.cpim";
connectAttr "rig:Spine1_M.rp" "rig:Spine1_M_parentConstraint1.crp";
connectAttr "rig:Spine1_M.rpt" "rig:Spine1_M_parentConstraint1.crt";
connectAttr "rig:Spine1_M.jo" "rig:Spine1_M_parentConstraint1.cjo";
connectAttr "rig:FKXSpine1_M.t" "rig:Spine1_M_parentConstraint1.tg[0].tt";
connectAttr "rig:FKXSpine1_M.rp" "rig:Spine1_M_parentConstraint1.tg[0].trp";
connectAttr "rig:FKXSpine1_M.rpt" "rig:Spine1_M_parentConstraint1.tg[0].trt";
connectAttr "rig:FKXSpine1_M.r" "rig:Spine1_M_parentConstraint1.tg[0].tr";
connectAttr "rig:FKXSpine1_M.ro" "rig:Spine1_M_parentConstraint1.tg[0].tro";
connectAttr "rig:FKXSpine1_M.s" "rig:Spine1_M_parentConstraint1.tg[0].ts";
connectAttr "rig:FKXSpine1_M.pm" "rig:Spine1_M_parentConstraint1.tg[0].tpm";
connectAttr "rig:FKXSpine1_M.jo" "rig:Spine1_M_parentConstraint1.tg[0].tjo";
connectAttr "rig:Spine1_M_parentConstraint1.w0" "rig:Spine1_M_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendSpineReverse_M.ox" "rig:Spine1_M_parentConstraint1.w0"
		;
connectAttr "rig:RootPart2_M.ro" "rig:RootPart2_M_parentConstraint1.cro";
connectAttr "rig:RootPart2_M.pim" "rig:RootPart2_M_parentConstraint1.cpim";
connectAttr "rig:RootPart2_M.rp" "rig:RootPart2_M_parentConstraint1.crp";
connectAttr "rig:RootPart2_M.rpt" "rig:RootPart2_M_parentConstraint1.crt";
connectAttr "rig:RootPart2_M.jo" "rig:RootPart2_M_parentConstraint1.cjo";
connectAttr "rig:FKXRootPart2_M.t" "rig:RootPart2_M_parentConstraint1.tg[0].tt";
connectAttr "rig:FKXRootPart2_M.rp" "rig:RootPart2_M_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXRootPart2_M.rpt" "rig:RootPart2_M_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXRootPart2_M.r" "rig:RootPart2_M_parentConstraint1.tg[0].tr";
connectAttr "rig:FKXRootPart2_M.ro" "rig:RootPart2_M_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXRootPart2_M.s" "rig:RootPart2_M_parentConstraint1.tg[0].ts";
connectAttr "rig:FKXRootPart2_M.pm" "rig:RootPart2_M_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXRootPart2_M.jo" "rig:RootPart2_M_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:RootPart2_M_parentConstraint1.w0" "rig:RootPart2_M_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendSpineReverse_M.ox" "rig:RootPart2_M_parentConstraint1.w0"
		;
connectAttr "rig:RootPart1_M.ro" "rig:RootPart1_M_parentConstraint1.cro";
connectAttr "rig:RootPart1_M.pim" "rig:RootPart1_M_parentConstraint1.cpim";
connectAttr "rig:RootPart1_M.rp" "rig:RootPart1_M_parentConstraint1.crp";
connectAttr "rig:RootPart1_M.rpt" "rig:RootPart1_M_parentConstraint1.crt";
connectAttr "rig:RootPart1_M.jo" "rig:RootPart1_M_parentConstraint1.cjo";
connectAttr "rig:FKXRootPart1_M.t" "rig:RootPart1_M_parentConstraint1.tg[0].tt";
connectAttr "rig:FKXRootPart1_M.rp" "rig:RootPart1_M_parentConstraint1.tg[0].trp"
		;
connectAttr "rig:FKXRootPart1_M.rpt" "rig:RootPart1_M_parentConstraint1.tg[0].trt"
		;
connectAttr "rig:FKXRootPart1_M.r" "rig:RootPart1_M_parentConstraint1.tg[0].tr";
connectAttr "rig:FKXRootPart1_M.ro" "rig:RootPart1_M_parentConstraint1.tg[0].tro"
		;
connectAttr "rig:FKXRootPart1_M.s" "rig:RootPart1_M_parentConstraint1.tg[0].ts";
connectAttr "rig:FKXRootPart1_M.pm" "rig:RootPart1_M_parentConstraint1.tg[0].tpm"
		;
connectAttr "rig:FKXRootPart1_M.jo" "rig:RootPart1_M_parentConstraint1.tg[0].tjo"
		;
connectAttr "rig:RootPart1_M_parentConstraint1.w0" "rig:RootPart1_M_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendSpineReverse_M.ox" "rig:RootPart1_M_parentConstraint1.w0"
		;
connectAttr "rig:Root_M.ro" "rig:Root_M_parentConstraint1.cro";
connectAttr "rig:Root_M.pim" "rig:Root_M_parentConstraint1.cpim";
connectAttr "rig:Root_M.rp" "rig:Root_M_parentConstraint1.crp";
connectAttr "rig:Root_M.rpt" "rig:Root_M_parentConstraint1.crt";
connectAttr "rig:Root_M.jo" "rig:Root_M_parentConstraint1.cjo";
connectAttr "rig:FKXRoot_M.t" "rig:Root_M_parentConstraint1.tg[0].tt";
connectAttr "rig:FKXRoot_M.rp" "rig:Root_M_parentConstraint1.tg[0].trp";
connectAttr "rig:FKXRoot_M.rpt" "rig:Root_M_parentConstraint1.tg[0].trt";
connectAttr "rig:FKXRoot_M.r" "rig:Root_M_parentConstraint1.tg[0].tr";
connectAttr "rig:FKXRoot_M.ro" "rig:Root_M_parentConstraint1.tg[0].tro";
connectAttr "rig:FKXRoot_M.s" "rig:Root_M_parentConstraint1.tg[0].ts";
connectAttr "rig:FKXRoot_M.pm" "rig:Root_M_parentConstraint1.tg[0].tpm";
connectAttr "rig:FKXRoot_M.jo" "rig:Root_M_parentConstraint1.tg[0].tjo";
connectAttr "rig:Root_M_parentConstraint1.w0" "rig:Root_M_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendSpineReverse_M.ox" "rig:Root_M_parentConstraint1.w0";
connectAttr "rig:Ankle_L.ro" "rig:Ankle_L_parentConstraint1.cro";
connectAttr "rig:Ankle_L.pim" "rig:Ankle_L_parentConstraint1.cpim";
connectAttr "rig:Ankle_L.rp" "rig:Ankle_L_parentConstraint1.crp";
connectAttr "rig:Ankle_L.rpt" "rig:Ankle_L_parentConstraint1.crt";
connectAttr "rig:Ankle_L.jo" "rig:Ankle_L_parentConstraint1.cjo";
connectAttr "rig:FKXAnkle_L.t" "rig:Ankle_L_parentConstraint1.tg[0].tt";
connectAttr "rig:FKXAnkle_L.rp" "rig:Ankle_L_parentConstraint1.tg[0].trp";
connectAttr "rig:FKXAnkle_L.rpt" "rig:Ankle_L_parentConstraint1.tg[0].trt";
connectAttr "rig:FKXAnkle_L.r" "rig:Ankle_L_parentConstraint1.tg[0].tr";
connectAttr "rig:FKXAnkle_L.ro" "rig:Ankle_L_parentConstraint1.tg[0].tro";
connectAttr "rig:FKXAnkle_L.s" "rig:Ankle_L_parentConstraint1.tg[0].ts";
connectAttr "rig:FKXAnkle_L.pm" "rig:Ankle_L_parentConstraint1.tg[0].tpm";
connectAttr "rig:FKXAnkle_L.jo" "rig:Ankle_L_parentConstraint1.tg[0].tjo";
connectAttr "rig:Ankle_L_parentConstraint1.w0" "rig:Ankle_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:Knee_L.ro" "rig:Knee_L_parentConstraint1.cro";
connectAttr "rig:Knee_L.pim" "rig:Knee_L_parentConstraint1.cpim";
connectAttr "rig:Knee_L.rp" "rig:Knee_L_parentConstraint1.crp";
connectAttr "rig:Knee_L.rpt" "rig:Knee_L_parentConstraint1.crt";
connectAttr "rig:Knee_L.jo" "rig:Knee_L_parentConstraint1.cjo";
connectAttr "rig:FKXKnee_L.t" "rig:Knee_L_parentConstraint1.tg[0].tt";
connectAttr "rig:FKXKnee_L.rp" "rig:Knee_L_parentConstraint1.tg[0].trp";
connectAttr "rig:FKXKnee_L.rpt" "rig:Knee_L_parentConstraint1.tg[0].trt";
connectAttr "rig:FKXKnee_L.r" "rig:Knee_L_parentConstraint1.tg[0].tr";
connectAttr "rig:FKXKnee_L.ro" "rig:Knee_L_parentConstraint1.tg[0].tro";
connectAttr "rig:FKXKnee_L.s" "rig:Knee_L_parentConstraint1.tg[0].ts";
connectAttr "rig:FKXKnee_L.pm" "rig:Knee_L_parentConstraint1.tg[0].tpm";
connectAttr "rig:FKXKnee_L.jo" "rig:Knee_L_parentConstraint1.tg[0].tjo";
connectAttr "rig:Knee_L_parentConstraint1.w0" "rig:Knee_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:Wrist_L.ro" "rig:Wrist_L_parentConstraint1.cro";
connectAttr "rig:Wrist_L.pim" "rig:Wrist_L_parentConstraint1.cpim";
connectAttr "rig:Wrist_L.rp" "rig:Wrist_L_parentConstraint1.crp";
connectAttr "rig:Wrist_L.rpt" "rig:Wrist_L_parentConstraint1.crt";
connectAttr "rig:Wrist_L.jo" "rig:Wrist_L_parentConstraint1.cjo";
connectAttr "rig:FKXWrist_L.t" "rig:Wrist_L_parentConstraint1.tg[0].tt";
connectAttr "rig:FKXWrist_L.rp" "rig:Wrist_L_parentConstraint1.tg[0].trp";
connectAttr "rig:FKXWrist_L.rpt" "rig:Wrist_L_parentConstraint1.tg[0].trt";
connectAttr "rig:FKXWrist_L.r" "rig:Wrist_L_parentConstraint1.tg[0].tr";
connectAttr "rig:FKXWrist_L.ro" "rig:Wrist_L_parentConstraint1.tg[0].tro";
connectAttr "rig:FKXWrist_L.s" "rig:Wrist_L_parentConstraint1.tg[0].ts";
connectAttr "rig:FKXWrist_L.pm" "rig:Wrist_L_parentConstraint1.tg[0].tpm";
connectAttr "rig:FKXWrist_L.jo" "rig:Wrist_L_parentConstraint1.tg[0].tjo";
connectAttr "rig:Wrist_L_parentConstraint1.w0" "rig:Wrist_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendArmReverse_L.ox" "rig:Wrist_L_parentConstraint1.w0";
connectAttr "rig:Scapula_L.ro" "rig:Scapula_L_parentConstraint1.cro";
connectAttr "rig:Scapula_L.pim" "rig:Scapula_L_parentConstraint1.cpim";
connectAttr "rig:Scapula_L.rp" "rig:Scapula_L_parentConstraint1.crp";
connectAttr "rig:Scapula_L.rpt" "rig:Scapula_L_parentConstraint1.crt";
connectAttr "rig:Scapula_L.jo" "rig:Scapula_L_parentConstraint1.cjo";
connectAttr "rig:FKXScapula_L.t" "rig:Scapula_L_parentConstraint1.tg[0].tt";
connectAttr "rig:FKXScapula_L.rp" "rig:Scapula_L_parentConstraint1.tg[0].trp";
connectAttr "rig:FKXScapula_L.rpt" "rig:Scapula_L_parentConstraint1.tg[0].trt";
connectAttr "rig:FKXScapula_L.r" "rig:Scapula_L_parentConstraint1.tg[0].tr";
connectAttr "rig:FKXScapula_L.ro" "rig:Scapula_L_parentConstraint1.tg[0].tro";
connectAttr "rig:FKXScapula_L.s" "rig:Scapula_L_parentConstraint1.tg[0].ts";
connectAttr "rig:FKXScapula_L.pm" "rig:Scapula_L_parentConstraint1.tg[0].tpm";
connectAttr "rig:FKXScapula_L.jo" "rig:Scapula_L_parentConstraint1.tg[0].tjo";
connectAttr "rig:Scapula_L_parentConstraint1.w0" "rig:Scapula_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:Breast_L.ro" "rig:Breast_L_parentConstraint1.cro";
connectAttr "rig:Breast_L.pim" "rig:Breast_L_parentConstraint1.cpim";
connectAttr "rig:Breast_L.rp" "rig:Breast_L_parentConstraint1.crp";
connectAttr "rig:Breast_L.rpt" "rig:Breast_L_parentConstraint1.crt";
connectAttr "rig:Breast_L.jo" "rig:Breast_L_parentConstraint1.cjo";
connectAttr "rig:FKXBreast_L.t" "rig:Breast_L_parentConstraint1.tg[0].tt";
connectAttr "rig:FKXBreast_L.rp" "rig:Breast_L_parentConstraint1.tg[0].trp";
connectAttr "rig:FKXBreast_L.rpt" "rig:Breast_L_parentConstraint1.tg[0].trt";
connectAttr "rig:FKXBreast_L.r" "rig:Breast_L_parentConstraint1.tg[0].tr";
connectAttr "rig:FKXBreast_L.ro" "rig:Breast_L_parentConstraint1.tg[0].tro";
connectAttr "rig:FKXBreast_L.s" "rig:Breast_L_parentConstraint1.tg[0].ts";
connectAttr "rig:FKXBreast_L.pm" "rig:Breast_L_parentConstraint1.tg[0].tpm";
connectAttr "rig:FKXBreast_L.jo" "rig:Breast_L_parentConstraint1.tg[0].tjo";
connectAttr "rig:Breast_L_parentConstraint1.w0" "rig:Breast_L_parentConstraint1.tg[0].tw"
		;
connectAttr "rig:Hip_R.pim" "rig:Hip_R_pointConstraint1.cpim";
connectAttr "rig:Hip_R.rp" "rig:Hip_R_pointConstraint1.crp";
connectAttr "rig:Hip_R.rpt" "rig:Hip_R_pointConstraint1.crt";
connectAttr "rig:FKXHip_R.t" "rig:Hip_R_pointConstraint1.tg[0].tt";
connectAttr "rig:FKXHip_R.rp" "rig:Hip_R_pointConstraint1.tg[0].trp";
connectAttr "rig:FKXHip_R.rpt" "rig:Hip_R_pointConstraint1.tg[0].trt";
connectAttr "rig:FKXHip_R.pm" "rig:Hip_R_pointConstraint1.tg[0].tpm";
connectAttr "rig:Hip_R_pointConstraint1.w0" "rig:Hip_R_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:Hip_R.ro" "rig:Hip_R_orientConstraint1.cro";
connectAttr "rig:Hip_R.pim" "rig:Hip_R_orientConstraint1.cpim";
connectAttr "rig:Hip_R.jo" "rig:Hip_R_orientConstraint1.cjo";
connectAttr "rig:TwisterHip0_R.r" "rig:Hip_R_orientConstraint1.tg[0].tr";
connectAttr "rig:TwisterHip0_R.ro" "rig:Hip_R_orientConstraint1.tg[0].tro";
connectAttr "rig:TwisterHip0_R.pm" "rig:Hip_R_orientConstraint1.tg[0].tpm";
connectAttr "rig:Hip_R_orientConstraint1.w0" "rig:Hip_R_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:HipPart1_R.ro" "rig:HipPart1_R_orientConstraint1.cro";
connectAttr "rig:HipPart1_R.pim" "rig:HipPart1_R_orientConstraint1.cpim";
connectAttr "rig:HipPart1_R.jo" "rig:HipPart1_R_orientConstraint1.cjo";
connectAttr "rig:TwisterHip1_R.r" "rig:HipPart1_R_orientConstraint1.tg[0].tr";
connectAttr "rig:TwisterHip1_R.ro" "rig:HipPart1_R_orientConstraint1.tg[0].tro";
connectAttr "rig:TwisterHip1_R.pm" "rig:HipPart1_R_orientConstraint1.tg[0].tpm";
connectAttr "rig:HipPart1_R_orientConstraint1.w0" "rig:HipPart1_R_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:HipPart2_R.ro" "rig:HipPart2_R_orientConstraint1.cro";
connectAttr "rig:HipPart2_R.pim" "rig:HipPart2_R_orientConstraint1.cpim";
connectAttr "rig:HipPart2_R.jo" "rig:HipPart2_R_orientConstraint1.cjo";
connectAttr "rig:TwisterHip2_R.r" "rig:HipPart2_R_orientConstraint1.tg[0].tr";
connectAttr "rig:TwisterHip2_R.ro" "rig:HipPart2_R_orientConstraint1.tg[0].tro";
connectAttr "rig:TwisterHip2_R.pm" "rig:HipPart2_R_orientConstraint1.tg[0].tpm";
connectAttr "rig:HipPart2_R_orientConstraint1.w0" "rig:HipPart2_R_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:Elbow_R.ro" "rig:Elbow_R_orientConstraint1.cro";
connectAttr "rig:Elbow_R.pim" "rig:Elbow_R_orientConstraint1.cpim";
connectAttr "rig:Elbow_R.jo" "rig:Elbow_R_orientConstraint1.cjo";
connectAttr "rig:TwisterElbow0_R.r" "rig:Elbow_R_orientConstraint1.tg[0].tr";
connectAttr "rig:TwisterElbow0_R.ro" "rig:Elbow_R_orientConstraint1.tg[0].tro";
connectAttr "rig:TwisterElbow0_R.pm" "rig:Elbow_R_orientConstraint1.tg[0].tpm";
connectAttr "rig:Elbow_R_orientConstraint1.w0" "rig:Elbow_R_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:ElbowPart1_R.ro" "rig:ElbowPart1_R_orientConstraint1.cro";
connectAttr "rig:ElbowPart1_R.pim" "rig:ElbowPart1_R_orientConstraint1.cpim";
connectAttr "rig:ElbowPart1_R.jo" "rig:ElbowPart1_R_orientConstraint1.cjo";
connectAttr "rig:TwisterElbow1_R.r" "rig:ElbowPart1_R_orientConstraint1.tg[0].tr"
		;
connectAttr "rig:TwisterElbow1_R.ro" "rig:ElbowPart1_R_orientConstraint1.tg[0].tro"
		;
connectAttr "rig:TwisterElbow1_R.pm" "rig:ElbowPart1_R_orientConstraint1.tg[0].tpm"
		;
connectAttr "rig:ElbowPart1_R_orientConstraint1.w0" "rig:ElbowPart1_R_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:ElbowPart2_R.ro" "rig:ElbowPart2_R_orientConstraint1.cro";
connectAttr "rig:ElbowPart2_R.pim" "rig:ElbowPart2_R_orientConstraint1.cpim";
connectAttr "rig:ElbowPart2_R.jo" "rig:ElbowPart2_R_orientConstraint1.cjo";
connectAttr "rig:TwisterElbow2_R.r" "rig:ElbowPart2_R_orientConstraint1.tg[0].tr"
		;
connectAttr "rig:TwisterElbow2_R.ro" "rig:ElbowPart2_R_orientConstraint1.tg[0].tro"
		;
connectAttr "rig:TwisterElbow2_R.pm" "rig:ElbowPart2_R_orientConstraint1.tg[0].tpm"
		;
connectAttr "rig:ElbowPart2_R_orientConstraint1.w0" "rig:ElbowPart2_R_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:Shoulder_R.ro" "rig:Shoulder_R_orientConstraint1.cro";
connectAttr "rig:Shoulder_R.pim" "rig:Shoulder_R_orientConstraint1.cpim";
connectAttr "rig:Shoulder_R.jo" "rig:Shoulder_R_orientConstraint1.cjo";
connectAttr "rig:TwisterShoulder0_R.r" "rig:Shoulder_R_orientConstraint1.tg[0].tr"
		;
connectAttr "rig:TwisterShoulder0_R.ro" "rig:Shoulder_R_orientConstraint1.tg[0].tro"
		;
connectAttr "rig:TwisterShoulder0_R.pm" "rig:Shoulder_R_orientConstraint1.tg[0].tpm"
		;
connectAttr "rig:Shoulder_R_orientConstraint1.w0" "rig:Shoulder_R_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:ShoulderPart1_R.ro" "rig:ShoulderPart1_R_orientConstraint1.cro"
		;
connectAttr "rig:ShoulderPart1_R.pim" "rig:ShoulderPart1_R_orientConstraint1.cpim"
		;
connectAttr "rig:ShoulderPart1_R.jo" "rig:ShoulderPart1_R_orientConstraint1.cjo"
		;
connectAttr "rig:TwisterShoulder1_R.r" "rig:ShoulderPart1_R_orientConstraint1.tg[0].tr"
		;
connectAttr "rig:TwisterShoulder1_R.ro" "rig:ShoulderPart1_R_orientConstraint1.tg[0].tro"
		;
connectAttr "rig:TwisterShoulder1_R.pm" "rig:ShoulderPart1_R_orientConstraint1.tg[0].tpm"
		;
connectAttr "rig:ShoulderPart1_R_orientConstraint1.w0" "rig:ShoulderPart1_R_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:ShoulderPart2_R.ro" "rig:ShoulderPart2_R_orientConstraint1.cro"
		;
connectAttr "rig:ShoulderPart2_R.pim" "rig:ShoulderPart2_R_orientConstraint1.cpim"
		;
connectAttr "rig:ShoulderPart2_R.jo" "rig:ShoulderPart2_R_orientConstraint1.cjo"
		;
connectAttr "rig:TwisterShoulder2_R.r" "rig:ShoulderPart2_R_orientConstraint1.tg[0].tr"
		;
connectAttr "rig:TwisterShoulder2_R.ro" "rig:ShoulderPart2_R_orientConstraint1.tg[0].tro"
		;
connectAttr "rig:TwisterShoulder2_R.pm" "rig:ShoulderPart2_R_orientConstraint1.tg[0].tpm"
		;
connectAttr "rig:ShoulderPart2_R_orientConstraint1.w0" "rig:ShoulderPart2_R_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:Hip_L.pim" "rig:Hip_L_pointConstraint1.cpim";
connectAttr "rig:Hip_L.rp" "rig:Hip_L_pointConstraint1.crp";
connectAttr "rig:Hip_L.rpt" "rig:Hip_L_pointConstraint1.crt";
connectAttr "rig:FKXHip_L.t" "rig:Hip_L_pointConstraint1.tg[0].tt";
connectAttr "rig:FKXHip_L.rp" "rig:Hip_L_pointConstraint1.tg[0].trp";
connectAttr "rig:FKXHip_L.rpt" "rig:Hip_L_pointConstraint1.tg[0].trt";
connectAttr "rig:FKXHip_L.pm" "rig:Hip_L_pointConstraint1.tg[0].tpm";
connectAttr "rig:Hip_L_pointConstraint1.w0" "rig:Hip_L_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:Hip_L.ro" "rig:Hip_L_orientConstraint1.cro";
connectAttr "rig:Hip_L.pim" "rig:Hip_L_orientConstraint1.cpim";
connectAttr "rig:Hip_L.jo" "rig:Hip_L_orientConstraint1.cjo";
connectAttr "rig:TwisterHip0_L.r" "rig:Hip_L_orientConstraint1.tg[0].tr";
connectAttr "rig:TwisterHip0_L.ro" "rig:Hip_L_orientConstraint1.tg[0].tro";
connectAttr "rig:TwisterHip0_L.pm" "rig:Hip_L_orientConstraint1.tg[0].tpm";
connectAttr "rig:Hip_L_orientConstraint1.w0" "rig:Hip_L_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:HipPart1_L.ro" "rig:HipPart1_L_orientConstraint1.cro";
connectAttr "rig:HipPart1_L.pim" "rig:HipPart1_L_orientConstraint1.cpim";
connectAttr "rig:HipPart1_L.jo" "rig:HipPart1_L_orientConstraint1.cjo";
connectAttr "rig:TwisterHip1_L.r" "rig:HipPart1_L_orientConstraint1.tg[0].tr";
connectAttr "rig:TwisterHip1_L.ro" "rig:HipPart1_L_orientConstraint1.tg[0].tro";
connectAttr "rig:TwisterHip1_L.pm" "rig:HipPart1_L_orientConstraint1.tg[0].tpm";
connectAttr "rig:HipPart1_L_orientConstraint1.w0" "rig:HipPart1_L_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:HipPart2_L.ro" "rig:HipPart2_L_orientConstraint1.cro";
connectAttr "rig:HipPart2_L.pim" "rig:HipPart2_L_orientConstraint1.cpim";
connectAttr "rig:HipPart2_L.jo" "rig:HipPart2_L_orientConstraint1.cjo";
connectAttr "rig:TwisterHip2_L.r" "rig:HipPart2_L_orientConstraint1.tg[0].tr";
connectAttr "rig:TwisterHip2_L.ro" "rig:HipPart2_L_orientConstraint1.tg[0].tro";
connectAttr "rig:TwisterHip2_L.pm" "rig:HipPart2_L_orientConstraint1.tg[0].tpm";
connectAttr "rig:HipPart2_L_orientConstraint1.w0" "rig:HipPart2_L_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:Elbow_L.pim" "rig:Elbow_L_pointConstraint1.cpim";
connectAttr "rig:Elbow_L.rp" "rig:Elbow_L_pointConstraint1.crp";
connectAttr "rig:Elbow_L.rpt" "rig:Elbow_L_pointConstraint1.crt";
connectAttr "rig:FKXElbow_L.t" "rig:Elbow_L_pointConstraint1.tg[0].tt";
connectAttr "rig:FKXElbow_L.rp" "rig:Elbow_L_pointConstraint1.tg[0].trp";
connectAttr "rig:FKXElbow_L.rpt" "rig:Elbow_L_pointConstraint1.tg[0].trt";
connectAttr "rig:FKXElbow_L.pm" "rig:Elbow_L_pointConstraint1.tg[0].tpm";
connectAttr "rig:Elbow_L_pointConstraint1.w0" "rig:Elbow_L_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendArmReverse_L.ox" "rig:Elbow_L_pointConstraint1.w0";
connectAttr "rig:Elbow_L.ro" "rig:Elbow_L_orientConstraint1.cro";
connectAttr "rig:Elbow_L.pim" "rig:Elbow_L_orientConstraint1.cpim";
connectAttr "rig:Elbow_L.jo" "rig:Elbow_L_orientConstraint1.cjo";
connectAttr "rig:TwisterElbow0_L.r" "rig:Elbow_L_orientConstraint1.tg[0].tr";
connectAttr "rig:TwisterElbow0_L.ro" "rig:Elbow_L_orientConstraint1.tg[0].tro";
connectAttr "rig:TwisterElbow0_L.pm" "rig:Elbow_L_orientConstraint1.tg[0].tpm";
connectAttr "rig:Elbow_L_orientConstraint1.w0" "rig:Elbow_L_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:ElbowPart1_L.ro" "rig:ElbowPart1_L_orientConstraint1.cro";
connectAttr "rig:ElbowPart1_L.pim" "rig:ElbowPart1_L_orientConstraint1.cpim";
connectAttr "rig:ElbowPart1_L.jo" "rig:ElbowPart1_L_orientConstraint1.cjo";
connectAttr "rig:TwisterElbow1_L.r" "rig:ElbowPart1_L_orientConstraint1.tg[0].tr"
		;
connectAttr "rig:TwisterElbow1_L.ro" "rig:ElbowPart1_L_orientConstraint1.tg[0].tro"
		;
connectAttr "rig:TwisterElbow1_L.pm" "rig:ElbowPart1_L_orientConstraint1.tg[0].tpm"
		;
connectAttr "rig:ElbowPart1_L_orientConstraint1.w0" "rig:ElbowPart1_L_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:ElbowPart2_L.ro" "rig:ElbowPart2_L_orientConstraint1.cro";
connectAttr "rig:ElbowPart2_L.pim" "rig:ElbowPart2_L_orientConstraint1.cpim";
connectAttr "rig:ElbowPart2_L.jo" "rig:ElbowPart2_L_orientConstraint1.cjo";
connectAttr "rig:TwisterElbow2_L.r" "rig:ElbowPart2_L_orientConstraint1.tg[0].tr"
		;
connectAttr "rig:TwisterElbow2_L.ro" "rig:ElbowPart2_L_orientConstraint1.tg[0].tro"
		;
connectAttr "rig:TwisterElbow2_L.pm" "rig:ElbowPart2_L_orientConstraint1.tg[0].tpm"
		;
connectAttr "rig:ElbowPart2_L_orientConstraint1.w0" "rig:ElbowPart2_L_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:Shoulder_L.pim" "rig:Shoulder_L_pointConstraint1.cpim";
connectAttr "rig:Shoulder_L.rp" "rig:Shoulder_L_pointConstraint1.crp";
connectAttr "rig:Shoulder_L.rpt" "rig:Shoulder_L_pointConstraint1.crt";
connectAttr "rig:FKXShoulder_L.t" "rig:Shoulder_L_pointConstraint1.tg[0].tt";
connectAttr "rig:FKXShoulder_L.rp" "rig:Shoulder_L_pointConstraint1.tg[0].trp";
connectAttr "rig:FKXShoulder_L.rpt" "rig:Shoulder_L_pointConstraint1.tg[0].trt";
connectAttr "rig:FKXShoulder_L.pm" "rig:Shoulder_L_pointConstraint1.tg[0].tpm";
connectAttr "rig:Shoulder_L_pointConstraint1.w0" "rig:Shoulder_L_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:FKIKBlendArmReverse_L.ox" "rig:Shoulder_L_pointConstraint1.w0";
connectAttr "rig:Shoulder_L.ro" "rig:Shoulder_L_orientConstraint1.cro";
connectAttr "rig:Shoulder_L.pim" "rig:Shoulder_L_orientConstraint1.cpim";
connectAttr "rig:Shoulder_L.jo" "rig:Shoulder_L_orientConstraint1.cjo";
connectAttr "rig:TwisterShoulder0_L.r" "rig:Shoulder_L_orientConstraint1.tg[0].tr"
		;
connectAttr "rig:TwisterShoulder0_L.ro" "rig:Shoulder_L_orientConstraint1.tg[0].tro"
		;
connectAttr "rig:TwisterShoulder0_L.pm" "rig:Shoulder_L_orientConstraint1.tg[0].tpm"
		;
connectAttr "rig:Shoulder_L_orientConstraint1.w0" "rig:Shoulder_L_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:ShoulderPart1_L.ro" "rig:ShoulderPart1_L_orientConstraint1.cro"
		;
connectAttr "rig:ShoulderPart1_L.pim" "rig:ShoulderPart1_L_orientConstraint1.cpim"
		;
connectAttr "rig:ShoulderPart1_L.jo" "rig:ShoulderPart1_L_orientConstraint1.cjo"
		;
connectAttr "rig:TwisterShoulder1_L.r" "rig:ShoulderPart1_L_orientConstraint1.tg[0].tr"
		;
connectAttr "rig:TwisterShoulder1_L.ro" "rig:ShoulderPart1_L_orientConstraint1.tg[0].tro"
		;
connectAttr "rig:TwisterShoulder1_L.pm" "rig:ShoulderPart1_L_orientConstraint1.tg[0].tpm"
		;
connectAttr "rig:ShoulderPart1_L_orientConstraint1.w0" "rig:ShoulderPart1_L_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:ShoulderPart2_L.ro" "rig:ShoulderPart2_L_orientConstraint1.cro"
		;
connectAttr "rig:ShoulderPart2_L.pim" "rig:ShoulderPart2_L_orientConstraint1.cpim"
		;
connectAttr "rig:ShoulderPart2_L.jo" "rig:ShoulderPart2_L_orientConstraint1.cjo"
		;
connectAttr "rig:TwisterShoulder2_L.r" "rig:ShoulderPart2_L_orientConstraint1.tg[0].tr"
		;
connectAttr "rig:TwisterShoulder2_L.ro" "rig:ShoulderPart2_L_orientConstraint1.tg[0].tro"
		;
connectAttr "rig:TwisterShoulder2_L.pm" "rig:ShoulderPart2_L_orientConstraint1.tg[0].tpm"
		;
connectAttr "rig:ShoulderPart2_L_orientConstraint1.w0" "rig:ShoulderPart2_L_orientConstraint1.tg[0].tw"
		;
connectAttr "rig:HipPart1_R.pim" "rig:HipPart1_R_pointConstraint1.cpim";
connectAttr "rig:HipPart1_R.rp" "rig:HipPart1_R_pointConstraint1.crp";
connectAttr "rig:HipPart1_R.rpt" "rig:HipPart1_R_pointConstraint1.crt";
connectAttr "rig:FKIKMixKnee_R.t" "rig:HipPart1_R_pointConstraint1.tg[0].tt";
connectAttr "rig:FKIKMixKnee_R.rp" "rig:HipPart1_R_pointConstraint1.tg[0].trp";
connectAttr "rig:FKIKMixKnee_R.rpt" "rig:HipPart1_R_pointConstraint1.tg[0].trt";
connectAttr "rig:FKIKMixKnee_R.pm" "rig:HipPart1_R_pointConstraint1.tg[0].tpm";
connectAttr "rig:HipPart1_R_pointConstraint1.w0" "rig:HipPart1_R_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:Hip_R.t" "rig:HipPart1_R_pointConstraint1.tg[1].tt";
connectAttr "rig:Hip_R.rp" "rig:HipPart1_R_pointConstraint1.tg[1].trp";
connectAttr "rig:Hip_R.rpt" "rig:HipPart1_R_pointConstraint1.tg[1].trt";
connectAttr "rig:Hip_R.pm" "rig:HipPart1_R_pointConstraint1.tg[1].tpm";
connectAttr "rig:HipPart1_R_pointConstraint1.w1" "rig:HipPart1_R_pointConstraint1.tg[1].tw"
		;
connectAttr "rig:HipPart2_R.pim" "rig:HipPart2_R_pointConstraint1.cpim";
connectAttr "rig:HipPart2_R.rp" "rig:HipPart2_R_pointConstraint1.crp";
connectAttr "rig:HipPart2_R.rpt" "rig:HipPart2_R_pointConstraint1.crt";
connectAttr "rig:FKIKMixKnee_R.t" "rig:HipPart2_R_pointConstraint1.tg[0].tt";
connectAttr "rig:FKIKMixKnee_R.rp" "rig:HipPart2_R_pointConstraint1.tg[0].trp";
connectAttr "rig:FKIKMixKnee_R.rpt" "rig:HipPart2_R_pointConstraint1.tg[0].trt";
connectAttr "rig:FKIKMixKnee_R.pm" "rig:HipPart2_R_pointConstraint1.tg[0].tpm";
connectAttr "rig:HipPart2_R_pointConstraint1.w0" "rig:HipPart2_R_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:Hip_R.t" "rig:HipPart2_R_pointConstraint1.tg[1].tt";
connectAttr "rig:Hip_R.rp" "rig:HipPart2_R_pointConstraint1.tg[1].trp";
connectAttr "rig:Hip_R.rpt" "rig:HipPart2_R_pointConstraint1.tg[1].trt";
connectAttr "rig:Hip_R.pm" "rig:HipPart2_R_pointConstraint1.tg[1].tpm";
connectAttr "rig:HipPart2_R_pointConstraint1.w1" "rig:HipPart2_R_pointConstraint1.tg[1].tw"
		;
connectAttr "rig:ElbowPart1_R.pim" "rig:ElbowPart1_R_pointConstraint1.cpim";
connectAttr "rig:ElbowPart1_R.rp" "rig:ElbowPart1_R_pointConstraint1.crp";
connectAttr "rig:ElbowPart1_R.rpt" "rig:ElbowPart1_R_pointConstraint1.crt";
connectAttr "rig:Elbow_R.t" "rig:ElbowPart1_R_pointConstraint1.tg[1].tt";
connectAttr "rig:Elbow_R.rp" "rig:ElbowPart1_R_pointConstraint1.tg[1].trp";
connectAttr "rig:Elbow_R.rpt" "rig:ElbowPart1_R_pointConstraint1.tg[1].trt";
connectAttr "rig:Elbow_R.pm" "rig:ElbowPart1_R_pointConstraint1.tg[1].tpm";
connectAttr "rig:ElbowPart1_R_pointConstraint1.w1" "rig:ElbowPart1_R_pointConstraint1.tg[1].tw"
		;
connectAttr "rig:ElbowPart2_R.pim" "rig:ElbowPart2_R_pointConstraint1.cpim";
connectAttr "rig:ElbowPart2_R.rp" "rig:ElbowPart2_R_pointConstraint1.crp";
connectAttr "rig:ElbowPart2_R.rpt" "rig:ElbowPart2_R_pointConstraint1.crt";
connectAttr "rig:Elbow_R.t" "rig:ElbowPart2_R_pointConstraint1.tg[1].tt";
connectAttr "rig:Elbow_R.rp" "rig:ElbowPart2_R_pointConstraint1.tg[1].trp";
connectAttr "rig:Elbow_R.rpt" "rig:ElbowPart2_R_pointConstraint1.tg[1].trt";
connectAttr "rig:Elbow_R.pm" "rig:ElbowPart2_R_pointConstraint1.tg[1].tpm";
connectAttr "rig:ElbowPart2_R_pointConstraint1.w1" "rig:ElbowPart2_R_pointConstraint1.tg[1].tw"
		;
connectAttr "rig:ShoulderPart1_R.pim" "rig:ShoulderPart1_R_pointConstraint1.cpim"
		;
connectAttr "rig:ShoulderPart1_R.rp" "rig:ShoulderPart1_R_pointConstraint1.crp";
connectAttr "rig:ShoulderPart1_R.rpt" "rig:ShoulderPart1_R_pointConstraint1.crt"
		;
connectAttr "rig:Shoulder_R.t" "rig:ShoulderPart1_R_pointConstraint1.tg[1].tt";
connectAttr "rig:Shoulder_R.rp" "rig:ShoulderPart1_R_pointConstraint1.tg[1].trp"
		;
connectAttr "rig:Shoulder_R.rpt" "rig:ShoulderPart1_R_pointConstraint1.tg[1].trt"
		;
connectAttr "rig:Shoulder_R.pm" "rig:ShoulderPart1_R_pointConstraint1.tg[1].tpm"
		;
connectAttr "rig:ShoulderPart1_R_pointConstraint1.w1" "rig:ShoulderPart1_R_pointConstraint1.tg[1].tw"
		;
connectAttr "rig:ShoulderPart2_R.pim" "rig:ShoulderPart2_R_pointConstraint1.cpim"
		;
connectAttr "rig:ShoulderPart2_R.rp" "rig:ShoulderPart2_R_pointConstraint1.crp";
connectAttr "rig:ShoulderPart2_R.rpt" "rig:ShoulderPart2_R_pointConstraint1.crt"
		;
connectAttr "rig:Shoulder_R.t" "rig:ShoulderPart2_R_pointConstraint1.tg[1].tt";
connectAttr "rig:Shoulder_R.rp" "rig:ShoulderPart2_R_pointConstraint1.tg[1].trp"
		;
connectAttr "rig:Shoulder_R.rpt" "rig:ShoulderPart2_R_pointConstraint1.tg[1].trt"
		;
connectAttr "rig:Shoulder_R.pm" "rig:ShoulderPart2_R_pointConstraint1.tg[1].tpm"
		;
connectAttr "rig:ShoulderPart2_R_pointConstraint1.w1" "rig:ShoulderPart2_R_pointConstraint1.tg[1].tw"
		;
connectAttr "rig:HipPart1_L.pim" "rig:HipPart1_L_pointConstraint1.cpim";
connectAttr "rig:HipPart1_L.rp" "rig:HipPart1_L_pointConstraint1.crp";
connectAttr "rig:HipPart1_L.rpt" "rig:HipPart1_L_pointConstraint1.crt";
connectAttr "rig:FKIKMixKnee_L.t" "rig:HipPart1_L_pointConstraint1.tg[0].tt";
connectAttr "rig:FKIKMixKnee_L.rp" "rig:HipPart1_L_pointConstraint1.tg[0].trp";
connectAttr "rig:FKIKMixKnee_L.rpt" "rig:HipPart1_L_pointConstraint1.tg[0].trt";
connectAttr "rig:FKIKMixKnee_L.pm" "rig:HipPart1_L_pointConstraint1.tg[0].tpm";
connectAttr "rig:HipPart1_L_pointConstraint1.w0" "rig:HipPart1_L_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:Hip_L.t" "rig:HipPart1_L_pointConstraint1.tg[1].tt";
connectAttr "rig:Hip_L.rp" "rig:HipPart1_L_pointConstraint1.tg[1].trp";
connectAttr "rig:Hip_L.rpt" "rig:HipPart1_L_pointConstraint1.tg[1].trt";
connectAttr "rig:Hip_L.pm" "rig:HipPart1_L_pointConstraint1.tg[1].tpm";
connectAttr "rig:HipPart1_L_pointConstraint1.w1" "rig:HipPart1_L_pointConstraint1.tg[1].tw"
		;
connectAttr "rig:HipPart2_L.pim" "rig:HipPart2_L_pointConstraint1.cpim";
connectAttr "rig:HipPart2_L.rp" "rig:HipPart2_L_pointConstraint1.crp";
connectAttr "rig:HipPart2_L.rpt" "rig:HipPart2_L_pointConstraint1.crt";
connectAttr "rig:FKIKMixKnee_L.t" "rig:HipPart2_L_pointConstraint1.tg[0].tt";
connectAttr "rig:FKIKMixKnee_L.rp" "rig:HipPart2_L_pointConstraint1.tg[0].trp";
connectAttr "rig:FKIKMixKnee_L.rpt" "rig:HipPart2_L_pointConstraint1.tg[0].trt";
connectAttr "rig:FKIKMixKnee_L.pm" "rig:HipPart2_L_pointConstraint1.tg[0].tpm";
connectAttr "rig:HipPart2_L_pointConstraint1.w0" "rig:HipPart2_L_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:Hip_L.t" "rig:HipPart2_L_pointConstraint1.tg[1].tt";
connectAttr "rig:Hip_L.rp" "rig:HipPart2_L_pointConstraint1.tg[1].trp";
connectAttr "rig:Hip_L.rpt" "rig:HipPart2_L_pointConstraint1.tg[1].trt";
connectAttr "rig:Hip_L.pm" "rig:HipPart2_L_pointConstraint1.tg[1].tpm";
connectAttr "rig:HipPart2_L_pointConstraint1.w1" "rig:HipPart2_L_pointConstraint1.tg[1].tw"
		;
connectAttr "rig:ElbowPart1_L.pim" "rig:ElbowPart1_L_pointConstraint1.cpim";
connectAttr "rig:ElbowPart1_L.rp" "rig:ElbowPart1_L_pointConstraint1.crp";
connectAttr "rig:ElbowPart1_L.rpt" "rig:ElbowPart1_L_pointConstraint1.crt";
connectAttr "rig:FKIKMixWrist_L.t" "rig:ElbowPart1_L_pointConstraint1.tg[0].tt";
connectAttr "rig:FKIKMixWrist_L.rp" "rig:ElbowPart1_L_pointConstraint1.tg[0].trp"
		;
connectAttr "rig:FKIKMixWrist_L.rpt" "rig:ElbowPart1_L_pointConstraint1.tg[0].trt"
		;
connectAttr "rig:FKIKMixWrist_L.pm" "rig:ElbowPart1_L_pointConstraint1.tg[0].tpm"
		;
connectAttr "rig:ElbowPart1_L_pointConstraint1.w0" "rig:ElbowPart1_L_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:Elbow_L.t" "rig:ElbowPart1_L_pointConstraint1.tg[1].tt";
connectAttr "rig:Elbow_L.rp" "rig:ElbowPart1_L_pointConstraint1.tg[1].trp";
connectAttr "rig:Elbow_L.rpt" "rig:ElbowPart1_L_pointConstraint1.tg[1].trt";
connectAttr "rig:Elbow_L.pm" "rig:ElbowPart1_L_pointConstraint1.tg[1].tpm";
connectAttr "rig:ElbowPart1_L_pointConstraint1.w1" "rig:ElbowPart1_L_pointConstraint1.tg[1].tw"
		;
connectAttr "rig:ElbowPart2_L.pim" "rig:ElbowPart2_L_pointConstraint1.cpim";
connectAttr "rig:ElbowPart2_L.rp" "rig:ElbowPart2_L_pointConstraint1.crp";
connectAttr "rig:ElbowPart2_L.rpt" "rig:ElbowPart2_L_pointConstraint1.crt";
connectAttr "rig:FKIKMixWrist_L.t" "rig:ElbowPart2_L_pointConstraint1.tg[0].tt";
connectAttr "rig:FKIKMixWrist_L.rp" "rig:ElbowPart2_L_pointConstraint1.tg[0].trp"
		;
connectAttr "rig:FKIKMixWrist_L.rpt" "rig:ElbowPart2_L_pointConstraint1.tg[0].trt"
		;
connectAttr "rig:FKIKMixWrist_L.pm" "rig:ElbowPart2_L_pointConstraint1.tg[0].tpm"
		;
connectAttr "rig:ElbowPart2_L_pointConstraint1.w0" "rig:ElbowPart2_L_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:Elbow_L.t" "rig:ElbowPart2_L_pointConstraint1.tg[1].tt";
connectAttr "rig:Elbow_L.rp" "rig:ElbowPart2_L_pointConstraint1.tg[1].trp";
connectAttr "rig:Elbow_L.rpt" "rig:ElbowPart2_L_pointConstraint1.tg[1].trt";
connectAttr "rig:Elbow_L.pm" "rig:ElbowPart2_L_pointConstraint1.tg[1].tpm";
connectAttr "rig:ElbowPart2_L_pointConstraint1.w1" "rig:ElbowPart2_L_pointConstraint1.tg[1].tw"
		;
connectAttr "rig:ShoulderPart1_L.pim" "rig:ShoulderPart1_L_pointConstraint1.cpim"
		;
connectAttr "rig:ShoulderPart1_L.rp" "rig:ShoulderPart1_L_pointConstraint1.crp";
connectAttr "rig:ShoulderPart1_L.rpt" "rig:ShoulderPart1_L_pointConstraint1.crt"
		;
connectAttr "rig:FKIKMixElbow_L.t" "rig:ShoulderPart1_L_pointConstraint1.tg[0].tt"
		;
connectAttr "rig:FKIKMixElbow_L.rp" "rig:ShoulderPart1_L_pointConstraint1.tg[0].trp"
		;
connectAttr "rig:FKIKMixElbow_L.rpt" "rig:ShoulderPart1_L_pointConstraint1.tg[0].trt"
		;
connectAttr "rig:FKIKMixElbow_L.pm" "rig:ShoulderPart1_L_pointConstraint1.tg[0].tpm"
		;
connectAttr "rig:ShoulderPart1_L_pointConstraint1.w0" "rig:ShoulderPart1_L_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:Shoulder_L.t" "rig:ShoulderPart1_L_pointConstraint1.tg[1].tt";
connectAttr "rig:Shoulder_L.rp" "rig:ShoulderPart1_L_pointConstraint1.tg[1].trp"
		;
connectAttr "rig:Shoulder_L.rpt" "rig:ShoulderPart1_L_pointConstraint1.tg[1].trt"
		;
connectAttr "rig:Shoulder_L.pm" "rig:ShoulderPart1_L_pointConstraint1.tg[1].tpm"
		;
connectAttr "rig:ShoulderPart1_L_pointConstraint1.w1" "rig:ShoulderPart1_L_pointConstraint1.tg[1].tw"
		;
connectAttr "rig:ShoulderPart2_L.pim" "rig:ShoulderPart2_L_pointConstraint1.cpim"
		;
connectAttr "rig:ShoulderPart2_L.rp" "rig:ShoulderPart2_L_pointConstraint1.crp";
connectAttr "rig:ShoulderPart2_L.rpt" "rig:ShoulderPart2_L_pointConstraint1.crt"
		;
connectAttr "rig:FKIKMixElbow_L.t" "rig:ShoulderPart2_L_pointConstraint1.tg[0].tt"
		;
connectAttr "rig:FKIKMixElbow_L.rp" "rig:ShoulderPart2_L_pointConstraint1.tg[0].trp"
		;
connectAttr "rig:FKIKMixElbow_L.rpt" "rig:ShoulderPart2_L_pointConstraint1.tg[0].trt"
		;
connectAttr "rig:FKIKMixElbow_L.pm" "rig:ShoulderPart2_L_pointConstraint1.tg[0].tpm"
		;
connectAttr "rig:ShoulderPart2_L_pointConstraint1.w0" "rig:ShoulderPart2_L_pointConstraint1.tg[0].tw"
		;
connectAttr "rig:Shoulder_L.t" "rig:ShoulderPart2_L_pointConstraint1.tg[1].tt";
connectAttr "rig:Shoulder_L.rp" "rig:ShoulderPart2_L_pointConstraint1.tg[1].trp"
		;
connectAttr "rig:Shoulder_L.rpt" "rig:ShoulderPart2_L_pointConstraint1.tg[1].trt"
		;
connectAttr "rig:Shoulder_L.pm" "rig:ShoulderPart2_L_pointConstraint1.tg[1].tpm"
		;
connectAttr "rig:ShoulderPart2_L_pointConstraint1.w1" "rig:ShoulderPart2_L_pointConstraint1.tg[1].tw"
		;
connectAttr "rig:Root_M_parentConstraint1.ctx" "rig:Root_M.tx";
connectAttr "rig:Root_M_parentConstraint1.cty" "rig:Root_M.ty";
connectAttr "rig:Root_M_parentConstraint1.ctz" "rig:Root_M.tz";
connectAttr "rig:Root_M_parentConstraint1.crx" "rig:Root_M.rx";
connectAttr "rig:Root_M_parentConstraint1.cry" "rig:Root_M.ry";
connectAttr "rig:Root_M_parentConstraint1.crz" "rig:Root_M.rz";
connectAttr "rig:ScaleBlendRoot_M.op" "rig:Root_M.s";
connectAttr "rig:jointLayer.di" "rig:Root_M.do";
connectAttr "rig:Hip_R_pointConstraint1.ctx" "rig:Hip_R.tx";
connectAttr "rig:Hip_R_pointConstraint1.cty" "rig:Hip_R.ty";
connectAttr "rig:Hip_R_pointConstraint1.ctz" "rig:Hip_R.tz";
connectAttr "rig:Hip_R_orientConstraint1.crx" "rig:Hip_R.rx";
connectAttr "rig:Hip_R_orientConstraint1.cry" "rig:Hip_R.ry";
connectAttr "rig:Hip_R_orientConstraint1.crz" "rig:Hip_R.rz";
connectAttr "rig:ScaleBlendHip_R.op" "rig:Hip_R.s";
connectAttr "rig:Root_M.s" "rig:Hip_R.is";
connectAttr "rig:Hip_R.s" "rig:HipPart1_R.is";
connectAttr "rig:Hip_R.sx" "rig:HipPart1_R.sx";
connectAttr "rig:Hip_R.sy" "rig:HipPart1_R.sy";
connectAttr "rig:Hip_R.sz" "rig:HipPart1_R.sz";
connectAttr "rig:HipPart1_R_orientConstraint1.crx" "rig:HipPart1_R.rx";
connectAttr "rig:HipPart1_R_orientConstraint1.cry" "rig:HipPart1_R.ry";
connectAttr "rig:HipPart1_R_orientConstraint1.crz" "rig:HipPart1_R.rz";
connectAttr "rig:HipPart1_R_pointConstraint1.ctx" "rig:HipPart1_R.tx";
connectAttr "rig:HipPart1_R_pointConstraint1.cty" "rig:HipPart1_R.ty";
connectAttr "rig:HipPart1_R_pointConstraint1.ctz" "rig:HipPart1_R.tz";
connectAttr "rig:HipPart1_R.s" "rig:HipPart2_R.is";
connectAttr "rig:Hip_R.sx" "rig:HipPart2_R.sx";
connectAttr "rig:Hip_R.sy" "rig:HipPart2_R.sy";
connectAttr "rig:Hip_R.sz" "rig:HipPart2_R.sz";
connectAttr "rig:HipPart2_R_orientConstraint1.crx" "rig:HipPart2_R.rx";
connectAttr "rig:HipPart2_R_orientConstraint1.cry" "rig:HipPart2_R.ry";
connectAttr "rig:HipPart2_R_orientConstraint1.crz" "rig:HipPart2_R.rz";
connectAttr "rig:HipPart2_R_pointConstraint1.ctx" "rig:HipPart2_R.tx";
connectAttr "rig:HipPart2_R_pointConstraint1.cty" "rig:HipPart2_R.ty";
connectAttr "rig:HipPart2_R_pointConstraint1.ctz" "rig:HipPart2_R.tz";
connectAttr "rig:ScaleBlendKnee_R.op" "rig:Knee_R.s";
connectAttr "rig:Knee_R_parentConstraint1.ctx" "rig:Knee_R.tx";
connectAttr "rig:Knee_R_parentConstraint1.cty" "rig:Knee_R.ty";
connectAttr "rig:Knee_R_parentConstraint1.ctz" "rig:Knee_R.tz";
connectAttr "rig:Knee_R_parentConstraint1.crx" "rig:Knee_R.rx";
connectAttr "rig:Knee_R_parentConstraint1.cry" "rig:Knee_R.ry";
connectAttr "rig:Knee_R_parentConstraint1.crz" "rig:Knee_R.rz";
connectAttr "rig:Ankle_R_parentConstraint1.ctx" "rig:Ankle_R.tx";
connectAttr "rig:Ankle_R_parentConstraint1.cty" "rig:Ankle_R.ty";
connectAttr "rig:Ankle_R_parentConstraint1.ctz" "rig:Ankle_R.tz";
connectAttr "rig:Ankle_R_parentConstraint1.crx" "rig:Ankle_R.rx";
connectAttr "rig:Ankle_R_parentConstraint1.cry" "rig:Ankle_R.ry";
connectAttr "rig:Ankle_R_parentConstraint1.crz" "rig:Ankle_R.rz";
connectAttr "rig:ScaleBlendAnkle_R.op" "rig:Ankle_R.s";
connectAttr "rig:Knee_R.s" "rig:Ankle_R.is";
connectAttr "rig:Ankle_R.s" "rig:Toes_R.is";
connectAttr "rig:Toes_R.s" "rig:ToesEnd_R.is";
connectAttr "rig:Hip_R.s" "rig:HipFat1_R.is";
connectAttr "rig:HipFat1_R.s" "rig:HipFatEnd_R.is";
connectAttr "rig:ScaleBlendRootPart1_M.op" "rig:RootPart1_M.s";
connectAttr "rig:Root_M.s" "rig:RootPart1_M.is";
connectAttr "rig:RootPart1_M_parentConstraint1.ctx" "rig:RootPart1_M.tx";
connectAttr "rig:RootPart1_M_parentConstraint1.cty" "rig:RootPart1_M.ty";
connectAttr "rig:RootPart1_M_parentConstraint1.ctz" "rig:RootPart1_M.tz";
connectAttr "rig:RootPart1_M_parentConstraint1.crx" "rig:RootPart1_M.rx";
connectAttr "rig:RootPart1_M_parentConstraint1.cry" "rig:RootPart1_M.ry";
connectAttr "rig:RootPart1_M_parentConstraint1.crz" "rig:RootPart1_M.rz";
connectAttr "rig:ScaleBlendRootPart2_M.op" "rig:RootPart2_M.s";
connectAttr "rig:RootPart1_M.s" "rig:RootPart2_M.is";
connectAttr "rig:RootPart2_M_parentConstraint1.ctx" "rig:RootPart2_M.tx";
connectAttr "rig:RootPart2_M_parentConstraint1.cty" "rig:RootPart2_M.ty";
connectAttr "rig:RootPart2_M_parentConstraint1.ctz" "rig:RootPart2_M.tz";
connectAttr "rig:RootPart2_M_parentConstraint1.crx" "rig:RootPart2_M.rx";
connectAttr "rig:RootPart2_M_parentConstraint1.cry" "rig:RootPart2_M.ry";
connectAttr "rig:RootPart2_M_parentConstraint1.crz" "rig:RootPart2_M.rz";
connectAttr "rig:ScaleBlendSpine1_M.op" "rig:Spine1_M.s";
connectAttr "rig:RootPart2_M.s" "rig:Spine1_M.is";
connectAttr "rig:Spine1_M_parentConstraint1.ctx" "rig:Spine1_M.tx";
connectAttr "rig:Spine1_M_parentConstraint1.cty" "rig:Spine1_M.ty";
connectAttr "rig:Spine1_M_parentConstraint1.ctz" "rig:Spine1_M.tz";
connectAttr "rig:Spine1_M_parentConstraint1.crx" "rig:Spine1_M.rx";
connectAttr "rig:Spine1_M_parentConstraint1.cry" "rig:Spine1_M.ry";
connectAttr "rig:Spine1_M_parentConstraint1.crz" "rig:Spine1_M.rz";
connectAttr "rig:Spine2_M_parentConstraint1.ctx" "rig:Spine2_M.tx";
connectAttr "rig:Spine2_M_parentConstraint1.cty" "rig:Spine2_M.ty";
connectAttr "rig:Spine2_M_parentConstraint1.ctz" "rig:Spine2_M.tz";
connectAttr "rig:Spine2_M_parentConstraint1.crx" "rig:Spine2_M.rx";
connectAttr "rig:Spine2_M_parentConstraint1.cry" "rig:Spine2_M.ry";
connectAttr "rig:Spine2_M_parentConstraint1.crz" "rig:Spine2_M.rz";
connectAttr "rig:ScaleBlendSpine2_M.op" "rig:Spine2_M.s";
connectAttr "rig:Spine1_M.s" "rig:Spine2_M.is";
connectAttr "rig:Chest_M_parentConstraint1.ctx" "rig:Chest_M.tx";
connectAttr "rig:Chest_M_parentConstraint1.cty" "rig:Chest_M.ty";
connectAttr "rig:Chest_M_parentConstraint1.ctz" "rig:Chest_M.tz";
connectAttr "rig:Chest_M_parentConstraint1.crx" "rig:Chest_M.rx";
connectAttr "rig:Chest_M_parentConstraint1.cry" "rig:Chest_M.ry";
connectAttr "rig:Chest_M_parentConstraint1.crz" "rig:Chest_M.rz";
connectAttr "rig:ScaleBlendChest_M.op" "rig:Chest_M.s";
connectAttr "rig:Spine2_M.s" "rig:Chest_M.is";
connectAttr "rig:Chest_M.s" "rig:Scapula_R.is";
connectAttr "rig:ScaleBlendShoulder_R.op" "rig:Shoulder_R.s";
connectAttr "rig:Scapula_R.s" "rig:Shoulder_R.is";
connectAttr "rig:Shoulder_R_orientConstraint1.crx" "rig:Shoulder_R.rx";
connectAttr "rig:Shoulder_R_orientConstraint1.cry" "rig:Shoulder_R.ry";
connectAttr "rig:Shoulder_R_orientConstraint1.crz" "rig:Shoulder_R.rz";
connectAttr "rig:Shoulder_R.s" "rig:ShoulderPart1_R.is";
connectAttr "rig:Shoulder_R.sx" "rig:ShoulderPart1_R.sx";
connectAttr "rig:Shoulder_R.sy" "rig:ShoulderPart1_R.sy";
connectAttr "rig:Shoulder_R.sz" "rig:ShoulderPart1_R.sz";
connectAttr "rig:ShoulderPart1_R_orientConstraint1.crx" "rig:ShoulderPart1_R.rx"
		;
connectAttr "rig:ShoulderPart1_R_orientConstraint1.cry" "rig:ShoulderPart1_R.ry"
		;
connectAttr "rig:ShoulderPart1_R_orientConstraint1.crz" "rig:ShoulderPart1_R.rz"
		;
connectAttr "rig:ShoulderPart1_R_pointConstraint1.ctx" "rig:ShoulderPart1_R.tx";
connectAttr "rig:ShoulderPart1_R_pointConstraint1.cty" "rig:ShoulderPart1_R.ty";
connectAttr "rig:ShoulderPart1_R_pointConstraint1.ctz" "rig:ShoulderPart1_R.tz";
connectAttr "rig:ShoulderPart1_R.s" "rig:ShoulderPart2_R.is";
connectAttr "rig:Shoulder_R.sx" "rig:ShoulderPart2_R.sx";
connectAttr "rig:Shoulder_R.sy" "rig:ShoulderPart2_R.sy";
connectAttr "rig:Shoulder_R.sz" "rig:ShoulderPart2_R.sz";
connectAttr "rig:ShoulderPart2_R_orientConstraint1.crx" "rig:ShoulderPart2_R.rx"
		;
connectAttr "rig:ShoulderPart2_R_orientConstraint1.cry" "rig:ShoulderPart2_R.ry"
		;
connectAttr "rig:ShoulderPart2_R_orientConstraint1.crz" "rig:ShoulderPart2_R.rz"
		;
connectAttr "rig:ShoulderPart2_R_pointConstraint1.ctx" "rig:ShoulderPart2_R.tx";
connectAttr "rig:ShoulderPart2_R_pointConstraint1.cty" "rig:ShoulderPart2_R.ty";
connectAttr "rig:ShoulderPart2_R_pointConstraint1.ctz" "rig:ShoulderPart2_R.tz";
connectAttr "rig:ScaleBlendElbow_R.op" "rig:Elbow_R.s";
connectAttr "rig:Elbow_R_orientConstraint1.crx" "rig:Elbow_R.rx";
connectAttr "rig:Elbow_R_orientConstraint1.cry" "rig:Elbow_R.ry";
connectAttr "rig:Elbow_R_orientConstraint1.crz" "rig:Elbow_R.rz";
connectAttr "rig:Elbow_R.s" "rig:ElbowPart1_R.is";
connectAttr "rig:Elbow_R.sx" "rig:ElbowPart1_R.sx";
connectAttr "rig:Elbow_R.sy" "rig:ElbowPart1_R.sy";
connectAttr "rig:Elbow_R.sz" "rig:ElbowPart1_R.sz";
connectAttr "rig:ElbowPart1_R_orientConstraint1.crx" "rig:ElbowPart1_R.rx";
connectAttr "rig:ElbowPart1_R_orientConstraint1.cry" "rig:ElbowPart1_R.ry";
connectAttr "rig:ElbowPart1_R_orientConstraint1.crz" "rig:ElbowPart1_R.rz";
connectAttr "rig:ElbowPart1_R_pointConstraint1.ctx" "rig:ElbowPart1_R.tx";
connectAttr "rig:ElbowPart1_R_pointConstraint1.cty" "rig:ElbowPart1_R.ty";
connectAttr "rig:ElbowPart1_R_pointConstraint1.ctz" "rig:ElbowPart1_R.tz";
connectAttr "rig:ElbowPart1_R.s" "rig:ElbowPart2_R.is";
connectAttr "rig:Elbow_R.sx" "rig:ElbowPart2_R.sx";
connectAttr "rig:Elbow_R.sy" "rig:ElbowPart2_R.sy";
connectAttr "rig:Elbow_R.sz" "rig:ElbowPart2_R.sz";
connectAttr "rig:ElbowPart2_R_orientConstraint1.crx" "rig:ElbowPart2_R.rx";
connectAttr "rig:ElbowPart2_R_orientConstraint1.cry" "rig:ElbowPart2_R.ry";
connectAttr "rig:ElbowPart2_R_orientConstraint1.crz" "rig:ElbowPart2_R.rz";
connectAttr "rig:ElbowPart2_R_pointConstraint1.ctx" "rig:ElbowPart2_R.tx";
connectAttr "rig:ElbowPart2_R_pointConstraint1.cty" "rig:ElbowPart2_R.ty";
connectAttr "rig:ElbowPart2_R_pointConstraint1.ctz" "rig:ElbowPart2_R.tz";
connectAttr "rig:ScaleBlendWrist_R.op" "rig:Wrist_R.s";
connectAttr "rig:FKIndexFinger1_R.s" "rig:IndexFinger1_R.s";
connectAttr "rig:Wrist_R.s" "rig:IndexFinger1_R.is";
connectAttr "rig:IndexFinger1_R_parentConstraint1.ctx" "rig:IndexFinger1_R.tx";
connectAttr "rig:IndexFinger1_R_parentConstraint1.cty" "rig:IndexFinger1_R.ty";
connectAttr "rig:IndexFinger1_R_parentConstraint1.ctz" "rig:IndexFinger1_R.tz";
connectAttr "rig:IndexFinger1_R_parentConstraint1.crx" "rig:IndexFinger1_R.rx";
connectAttr "rig:IndexFinger1_R_parentConstraint1.cry" "rig:IndexFinger1_R.ry";
connectAttr "rig:IndexFinger1_R_parentConstraint1.crz" "rig:IndexFinger1_R.rz";
connectAttr "rig:FKIndexFinger2_R.s" "rig:IndexFinger2_R.s";
connectAttr "rig:IndexFinger1_R.s" "rig:IndexFinger2_R.is";
connectAttr "rig:IndexFinger2_R_parentConstraint1.ctx" "rig:IndexFinger2_R.tx";
connectAttr "rig:IndexFinger2_R_parentConstraint1.cty" "rig:IndexFinger2_R.ty";
connectAttr "rig:IndexFinger2_R_parentConstraint1.ctz" "rig:IndexFinger2_R.tz";
connectAttr "rig:IndexFinger2_R_parentConstraint1.crx" "rig:IndexFinger2_R.rx";
connectAttr "rig:IndexFinger2_R_parentConstraint1.cry" "rig:IndexFinger2_R.ry";
connectAttr "rig:IndexFinger2_R_parentConstraint1.crz" "rig:IndexFinger2_R.rz";
connectAttr "rig:FKIndexFinger3_R.s" "rig:IndexFinger3_R.s";
connectAttr "rig:IndexFinger2_R.s" "rig:IndexFinger3_R.is";
connectAttr "rig:IndexFinger3_R_parentConstraint1.ctx" "rig:IndexFinger3_R.tx";
connectAttr "rig:IndexFinger3_R_parentConstraint1.cty" "rig:IndexFinger3_R.ty";
connectAttr "rig:IndexFinger3_R_parentConstraint1.ctz" "rig:IndexFinger3_R.tz";
connectAttr "rig:IndexFinger3_R_parentConstraint1.crx" "rig:IndexFinger3_R.rx";
connectAttr "rig:IndexFinger3_R_parentConstraint1.cry" "rig:IndexFinger3_R.ry";
connectAttr "rig:IndexFinger3_R_parentConstraint1.crz" "rig:IndexFinger3_R.rz";
connectAttr "rig:IndexFinger3_R.s" "rig:IndexFinger4_R.is";
connectAttr "rig:FKMiddleFinger1_R.s" "rig:MiddleFinger1_R.s";
connectAttr "rig:Wrist_R.s" "rig:MiddleFinger1_R.is";
connectAttr "rig:MiddleFinger1_R_parentConstraint1.ctx" "rig:MiddleFinger1_R.tx"
		;
connectAttr "rig:MiddleFinger1_R_parentConstraint1.cty" "rig:MiddleFinger1_R.ty"
		;
connectAttr "rig:MiddleFinger1_R_parentConstraint1.ctz" "rig:MiddleFinger1_R.tz"
		;
connectAttr "rig:MiddleFinger1_R_parentConstraint1.crx" "rig:MiddleFinger1_R.rx"
		;
connectAttr "rig:MiddleFinger1_R_parentConstraint1.cry" "rig:MiddleFinger1_R.ry"
		;
connectAttr "rig:MiddleFinger1_R_parentConstraint1.crz" "rig:MiddleFinger1_R.rz"
		;
connectAttr "rig:FKMiddleFinger2_R.s" "rig:MiddleFinger2_R.s";
connectAttr "rig:MiddleFinger1_R.s" "rig:MiddleFinger2_R.is";
connectAttr "rig:MiddleFinger2_R_parentConstraint1.ctx" "rig:MiddleFinger2_R.tx"
		;
connectAttr "rig:MiddleFinger2_R_parentConstraint1.cty" "rig:MiddleFinger2_R.ty"
		;
connectAttr "rig:MiddleFinger2_R_parentConstraint1.ctz" "rig:MiddleFinger2_R.tz"
		;
connectAttr "rig:MiddleFinger2_R_parentConstraint1.crx" "rig:MiddleFinger2_R.rx"
		;
connectAttr "rig:MiddleFinger2_R_parentConstraint1.cry" "rig:MiddleFinger2_R.ry"
		;
connectAttr "rig:MiddleFinger2_R_parentConstraint1.crz" "rig:MiddleFinger2_R.rz"
		;
connectAttr "rig:FKMiddleFinger3_R.s" "rig:MiddleFinger3_R.s";
connectAttr "rig:MiddleFinger2_R.s" "rig:MiddleFinger3_R.is";
connectAttr "rig:MiddleFinger3_R_parentConstraint1.ctx" "rig:MiddleFinger3_R.tx"
		;
connectAttr "rig:MiddleFinger3_R_parentConstraint1.cty" "rig:MiddleFinger3_R.ty"
		;
connectAttr "rig:MiddleFinger3_R_parentConstraint1.ctz" "rig:MiddleFinger3_R.tz"
		;
connectAttr "rig:MiddleFinger3_R_parentConstraint1.crx" "rig:MiddleFinger3_R.rx"
		;
connectAttr "rig:MiddleFinger3_R_parentConstraint1.cry" "rig:MiddleFinger3_R.ry"
		;
connectAttr "rig:MiddleFinger3_R_parentConstraint1.crz" "rig:MiddleFinger3_R.rz"
		;
connectAttr "rig:MiddleFinger3_R.s" "rig:MiddleFinger4_R.is";
connectAttr "rig:FKCup_R.s" "rig:Cup_R.s";
connectAttr "rig:Wrist_R.s" "rig:Cup_R.is";
connectAttr "rig:Cup_R_parentConstraint1.ctx" "rig:Cup_R.tx";
connectAttr "rig:Cup_R_parentConstraint1.cty" "rig:Cup_R.ty";
connectAttr "rig:Cup_R_parentConstraint1.ctz" "rig:Cup_R.tz";
connectAttr "rig:Cup_R_parentConstraint1.crx" "rig:Cup_R.rx";
connectAttr "rig:Cup_R_parentConstraint1.cry" "rig:Cup_R.ry";
connectAttr "rig:Cup_R_parentConstraint1.crz" "rig:Cup_R.rz";
connectAttr "rig:FKPinkyFinger1_R.s" "rig:PinkyFinger1_R.s";
connectAttr "rig:Cup_R.s" "rig:PinkyFinger1_R.is";
connectAttr "rig:PinkyFinger1_R_parentConstraint1.ctx" "rig:PinkyFinger1_R.tx";
connectAttr "rig:PinkyFinger1_R_parentConstraint1.cty" "rig:PinkyFinger1_R.ty";
connectAttr "rig:PinkyFinger1_R_parentConstraint1.ctz" "rig:PinkyFinger1_R.tz";
connectAttr "rig:PinkyFinger1_R_parentConstraint1.crx" "rig:PinkyFinger1_R.rx";
connectAttr "rig:PinkyFinger1_R_parentConstraint1.cry" "rig:PinkyFinger1_R.ry";
connectAttr "rig:PinkyFinger1_R_parentConstraint1.crz" "rig:PinkyFinger1_R.rz";
connectAttr "rig:FKPinkyFinger2_R.s" "rig:PinkyFinger2_R.s";
connectAttr "rig:PinkyFinger1_R.s" "rig:PinkyFinger2_R.is";
connectAttr "rig:PinkyFinger2_R_parentConstraint1.ctx" "rig:PinkyFinger2_R.tx";
connectAttr "rig:PinkyFinger2_R_parentConstraint1.cty" "rig:PinkyFinger2_R.ty";
connectAttr "rig:PinkyFinger2_R_parentConstraint1.ctz" "rig:PinkyFinger2_R.tz";
connectAttr "rig:PinkyFinger2_R_parentConstraint1.crx" "rig:PinkyFinger2_R.rx";
connectAttr "rig:PinkyFinger2_R_parentConstraint1.cry" "rig:PinkyFinger2_R.ry";
connectAttr "rig:PinkyFinger2_R_parentConstraint1.crz" "rig:PinkyFinger2_R.rz";
connectAttr "rig:FKPinkyFinger3_R.s" "rig:PinkyFinger3_R.s";
connectAttr "rig:PinkyFinger2_R.s" "rig:PinkyFinger3_R.is";
connectAttr "rig:PinkyFinger3_R_parentConstraint1.ctx" "rig:PinkyFinger3_R.tx";
connectAttr "rig:PinkyFinger3_R_parentConstraint1.cty" "rig:PinkyFinger3_R.ty";
connectAttr "rig:PinkyFinger3_R_parentConstraint1.ctz" "rig:PinkyFinger3_R.tz";
connectAttr "rig:PinkyFinger3_R_parentConstraint1.crx" "rig:PinkyFinger3_R.rx";
connectAttr "rig:PinkyFinger3_R_parentConstraint1.cry" "rig:PinkyFinger3_R.ry";
connectAttr "rig:PinkyFinger3_R_parentConstraint1.crz" "rig:PinkyFinger3_R.rz";
connectAttr "rig:PinkyFinger3_R.s" "rig:PinkyFinger4_R.is";
connectAttr "rig:FKRingFinger1_R.s" "rig:RingFinger1_R.s";
connectAttr "rig:Cup_R.s" "rig:RingFinger1_R.is";
connectAttr "rig:RingFinger1_R_parentConstraint1.ctx" "rig:RingFinger1_R.tx";
connectAttr "rig:RingFinger1_R_parentConstraint1.cty" "rig:RingFinger1_R.ty";
connectAttr "rig:RingFinger1_R_parentConstraint1.ctz" "rig:RingFinger1_R.tz";
connectAttr "rig:RingFinger1_R_parentConstraint1.crx" "rig:RingFinger1_R.rx";
connectAttr "rig:RingFinger1_R_parentConstraint1.cry" "rig:RingFinger1_R.ry";
connectAttr "rig:RingFinger1_R_parentConstraint1.crz" "rig:RingFinger1_R.rz";
connectAttr "rig:FKRingFinger2_R.s" "rig:RingFinger2_R.s";
connectAttr "rig:RingFinger1_R.s" "rig:RingFinger2_R.is";
connectAttr "rig:RingFinger2_R_parentConstraint1.ctx" "rig:RingFinger2_R.tx";
connectAttr "rig:RingFinger2_R_parentConstraint1.cty" "rig:RingFinger2_R.ty";
connectAttr "rig:RingFinger2_R_parentConstraint1.ctz" "rig:RingFinger2_R.tz";
connectAttr "rig:RingFinger2_R_parentConstraint1.crx" "rig:RingFinger2_R.rx";
connectAttr "rig:RingFinger2_R_parentConstraint1.cry" "rig:RingFinger2_R.ry";
connectAttr "rig:RingFinger2_R_parentConstraint1.crz" "rig:RingFinger2_R.rz";
connectAttr "rig:FKRingFinger3_R.s" "rig:RingFinger3_R.s";
connectAttr "rig:RingFinger2_R.s" "rig:RingFinger3_R.is";
connectAttr "rig:RingFinger3_R_parentConstraint1.ctx" "rig:RingFinger3_R.tx";
connectAttr "rig:RingFinger3_R_parentConstraint1.cty" "rig:RingFinger3_R.ty";
connectAttr "rig:RingFinger3_R_parentConstraint1.ctz" "rig:RingFinger3_R.tz";
connectAttr "rig:RingFinger3_R_parentConstraint1.crx" "rig:RingFinger3_R.rx";
connectAttr "rig:RingFinger3_R_parentConstraint1.cry" "rig:RingFinger3_R.ry";
connectAttr "rig:RingFinger3_R_parentConstraint1.crz" "rig:RingFinger3_R.rz";
connectAttr "rig:RingFinger3_R.s" "rig:RingFinger4_R.is";
connectAttr "rig:FKThumbFinger1_R.s" "rig:ThumbFinger1_R.s";
connectAttr "rig:Wrist_R.s" "rig:ThumbFinger1_R.is";
connectAttr "rig:ThumbFinger1_R_parentConstraint1.ctx" "rig:ThumbFinger1_R.tx";
connectAttr "rig:ThumbFinger1_R_parentConstraint1.cty" "rig:ThumbFinger1_R.ty";
connectAttr "rig:ThumbFinger1_R_parentConstraint1.ctz" "rig:ThumbFinger1_R.tz";
connectAttr "rig:ThumbFinger1_R_parentConstraint1.crx" "rig:ThumbFinger1_R.rx";
connectAttr "rig:ThumbFinger1_R_parentConstraint1.cry" "rig:ThumbFinger1_R.ry";
connectAttr "rig:ThumbFinger1_R_parentConstraint1.crz" "rig:ThumbFinger1_R.rz";
connectAttr "rig:FKThumbFinger2_R.s" "rig:ThumbFinger2_R.s";
connectAttr "rig:ThumbFinger1_R.s" "rig:ThumbFinger2_R.is";
connectAttr "rig:ThumbFinger2_R_parentConstraint1.ctx" "rig:ThumbFinger2_R.tx";
connectAttr "rig:ThumbFinger2_R_parentConstraint1.cty" "rig:ThumbFinger2_R.ty";
connectAttr "rig:ThumbFinger2_R_parentConstraint1.ctz" "rig:ThumbFinger2_R.tz";
connectAttr "rig:ThumbFinger2_R_parentConstraint1.crx" "rig:ThumbFinger2_R.rx";
connectAttr "rig:ThumbFinger2_R_parentConstraint1.cry" "rig:ThumbFinger2_R.ry";
connectAttr "rig:ThumbFinger2_R_parentConstraint1.crz" "rig:ThumbFinger2_R.rz";
connectAttr "rig:FKThumbFinger3_R.s" "rig:ThumbFinger3_R.s";
connectAttr "rig:ThumbFinger2_R.s" "rig:ThumbFinger3_R.is";
connectAttr "rig:ThumbFinger3_R_parentConstraint1.ctx" "rig:ThumbFinger3_R.tx";
connectAttr "rig:ThumbFinger3_R_parentConstraint1.cty" "rig:ThumbFinger3_R.ty";
connectAttr "rig:ThumbFinger3_R_parentConstraint1.ctz" "rig:ThumbFinger3_R.tz";
connectAttr "rig:ThumbFinger3_R_parentConstraint1.crx" "rig:ThumbFinger3_R.rx";
connectAttr "rig:ThumbFinger3_R_parentConstraint1.cry" "rig:ThumbFinger3_R.ry";
connectAttr "rig:ThumbFinger3_R_parentConstraint1.crz" "rig:ThumbFinger3_R.rz";
connectAttr "rig:ThumbFinger3_R.s" "rig:ThumbFinger4_R.is";
connectAttr "rig:Chest_M.s" "rig:Neck_M.is";
connectAttr "rig:Neck_M.s" "rig:NeckPart1_M.is";
connectAttr "rig:NeckPart1_M_parentConstraint1.ctx" "rig:NeckPart1_M.tx";
connectAttr "rig:NeckPart1_M_parentConstraint1.cty" "rig:NeckPart1_M.ty";
connectAttr "rig:NeckPart1_M_parentConstraint1.ctz" "rig:NeckPart1_M.tz";
connectAttr "rig:NeckPart1_M_parentConstraint1.crx" "rig:NeckPart1_M.rx";
connectAttr "rig:NeckPart1_M_parentConstraint1.cry" "rig:NeckPart1_M.ry";
connectAttr "rig:NeckPart1_M_parentConstraint1.crz" "rig:NeckPart1_M.rz";
connectAttr "rig:NeckPart1_M.s" "rig:NeckPart2_M.is";
connectAttr "rig:NeckPart2_M_parentConstraint1.ctx" "rig:NeckPart2_M.tx";
connectAttr "rig:NeckPart2_M_parentConstraint1.cty" "rig:NeckPart2_M.ty";
connectAttr "rig:NeckPart2_M_parentConstraint1.ctz" "rig:NeckPart2_M.tz";
connectAttr "rig:NeckPart2_M_parentConstraint1.crx" "rig:NeckPart2_M.rx";
connectAttr "rig:NeckPart2_M_parentConstraint1.cry" "rig:NeckPart2_M.ry";
connectAttr "rig:NeckPart2_M_parentConstraint1.crz" "rig:NeckPart2_M.rz";
connectAttr "rig:NeckPart2_M.s" "rig:Neck1_M.is";
connectAttr "rig:Neck1_M.s" "rig:Neck2_M.is";
connectAttr "rig:Neck2_M.s" "rig:Head_M.is";
connectAttr "rig:Head_M.s" "rig:HeadEnd_M.is";
connectAttr "rig:Scapula_L_parentConstraint1.ctx" "rig:Scapula_L.tx";
connectAttr "rig:Scapula_L_parentConstraint1.cty" "rig:Scapula_L.ty";
connectAttr "rig:Scapula_L_parentConstraint1.ctz" "rig:Scapula_L.tz";
connectAttr "rig:Scapula_L_parentConstraint1.crx" "rig:Scapula_L.rx";
connectAttr "rig:Scapula_L_parentConstraint1.cry" "rig:Scapula_L.ry";
connectAttr "rig:Scapula_L_parentConstraint1.crz" "rig:Scapula_L.rz";
connectAttr "rig:FKScapula_L.s" "rig:Scapula_L.s";
connectAttr "rig:Chest_M.s" "rig:Scapula_L.is";
connectAttr "rig:Shoulder_L_pointConstraint1.ctx" "rig:Shoulder_L.tx";
connectAttr "rig:Shoulder_L_pointConstraint1.cty" "rig:Shoulder_L.ty";
connectAttr "rig:Shoulder_L_pointConstraint1.ctz" "rig:Shoulder_L.tz";
connectAttr "rig:ScaleBlendShoulder_L.op" "rig:Shoulder_L.s";
connectAttr "rig:Scapula_L.s" "rig:Shoulder_L.is";
connectAttr "rig:Shoulder_L_orientConstraint1.crx" "rig:Shoulder_L.rx";
connectAttr "rig:Shoulder_L_orientConstraint1.cry" "rig:Shoulder_L.ry";
connectAttr "rig:Shoulder_L_orientConstraint1.crz" "rig:Shoulder_L.rz";
connectAttr "rig:Shoulder_L.s" "rig:ShoulderPart1_L.is";
connectAttr "rig:Shoulder_L.sx" "rig:ShoulderPart1_L.sx";
connectAttr "rig:Shoulder_L.sy" "rig:ShoulderPart1_L.sy";
connectAttr "rig:Shoulder_L.sz" "rig:ShoulderPart1_L.sz";
connectAttr "rig:ShoulderPart1_L_orientConstraint1.crx" "rig:ShoulderPart1_L.rx"
		;
connectAttr "rig:ShoulderPart1_L_orientConstraint1.cry" "rig:ShoulderPart1_L.ry"
		;
connectAttr "rig:ShoulderPart1_L_orientConstraint1.crz" "rig:ShoulderPart1_L.rz"
		;
connectAttr "rig:ShoulderPart1_L_pointConstraint1.ctx" "rig:ShoulderPart1_L.tx";
connectAttr "rig:ShoulderPart1_L_pointConstraint1.cty" "rig:ShoulderPart1_L.ty";
connectAttr "rig:ShoulderPart1_L_pointConstraint1.ctz" "rig:ShoulderPart1_L.tz";
connectAttr "rig:ShoulderPart1_L.s" "rig:ShoulderPart2_L.is";
connectAttr "rig:Shoulder_L.sx" "rig:ShoulderPart2_L.sx";
connectAttr "rig:Shoulder_L.sy" "rig:ShoulderPart2_L.sy";
connectAttr "rig:Shoulder_L.sz" "rig:ShoulderPart2_L.sz";
connectAttr "rig:ShoulderPart2_L_orientConstraint1.crx" "rig:ShoulderPart2_L.rx"
		;
connectAttr "rig:ShoulderPart2_L_orientConstraint1.cry" "rig:ShoulderPart2_L.ry"
		;
connectAttr "rig:ShoulderPart2_L_orientConstraint1.crz" "rig:ShoulderPart2_L.rz"
		;
connectAttr "rig:ShoulderPart2_L_pointConstraint1.ctx" "rig:ShoulderPart2_L.tx";
connectAttr "rig:ShoulderPart2_L_pointConstraint1.cty" "rig:ShoulderPart2_L.ty";
connectAttr "rig:ShoulderPart2_L_pointConstraint1.ctz" "rig:ShoulderPart2_L.tz";
connectAttr "rig:Elbow_L_pointConstraint1.ctx" "rig:Elbow_L.tx";
connectAttr "rig:Elbow_L_pointConstraint1.cty" "rig:Elbow_L.ty";
connectAttr "rig:Elbow_L_pointConstraint1.ctz" "rig:Elbow_L.tz";
connectAttr "rig:ScaleBlendElbow_L.op" "rig:Elbow_L.s";
connectAttr "rig:Elbow_L_orientConstraint1.crx" "rig:Elbow_L.rx";
connectAttr "rig:Elbow_L_orientConstraint1.cry" "rig:Elbow_L.ry";
connectAttr "rig:Elbow_L_orientConstraint1.crz" "rig:Elbow_L.rz";
connectAttr "rig:Elbow_L.s" "rig:ElbowPart1_L.is";
connectAttr "rig:Elbow_L.sx" "rig:ElbowPart1_L.sx";
connectAttr "rig:Elbow_L.sy" "rig:ElbowPart1_L.sy";
connectAttr "rig:Elbow_L.sz" "rig:ElbowPart1_L.sz";
connectAttr "rig:ElbowPart1_L_orientConstraint1.crx" "rig:ElbowPart1_L.rx";
connectAttr "rig:ElbowPart1_L_orientConstraint1.cry" "rig:ElbowPart1_L.ry";
connectAttr "rig:ElbowPart1_L_orientConstraint1.crz" "rig:ElbowPart1_L.rz";
connectAttr "rig:ElbowPart1_L_pointConstraint1.ctx" "rig:ElbowPart1_L.tx";
connectAttr "rig:ElbowPart1_L_pointConstraint1.cty" "rig:ElbowPart1_L.ty";
connectAttr "rig:ElbowPart1_L_pointConstraint1.ctz" "rig:ElbowPart1_L.tz";
connectAttr "rig:ElbowPart1_L.s" "rig:ElbowPart2_L.is";
connectAttr "rig:Elbow_L.sx" "rig:ElbowPart2_L.sx";
connectAttr "rig:Elbow_L.sy" "rig:ElbowPart2_L.sy";
connectAttr "rig:Elbow_L.sz" "rig:ElbowPart2_L.sz";
connectAttr "rig:ElbowPart2_L_orientConstraint1.crx" "rig:ElbowPart2_L.rx";
connectAttr "rig:ElbowPart2_L_orientConstraint1.cry" "rig:ElbowPart2_L.ry";
connectAttr "rig:ElbowPart2_L_orientConstraint1.crz" "rig:ElbowPart2_L.rz";
connectAttr "rig:ElbowPart2_L_pointConstraint1.ctx" "rig:ElbowPart2_L.tx";
connectAttr "rig:ElbowPart2_L_pointConstraint1.cty" "rig:ElbowPart2_L.ty";
connectAttr "rig:ElbowPart2_L_pointConstraint1.ctz" "rig:ElbowPart2_L.tz";
connectAttr "rig:Wrist_L_parentConstraint1.ctx" "rig:Wrist_L.tx";
connectAttr "rig:Wrist_L_parentConstraint1.cty" "rig:Wrist_L.ty";
connectAttr "rig:Wrist_L_parentConstraint1.ctz" "rig:Wrist_L.tz";
connectAttr "rig:Wrist_L_parentConstraint1.crx" "rig:Wrist_L.rx";
connectAttr "rig:Wrist_L_parentConstraint1.cry" "rig:Wrist_L.ry";
connectAttr "rig:Wrist_L_parentConstraint1.crz" "rig:Wrist_L.rz";
connectAttr "rig:ScaleBlendWrist_L.op" "rig:Wrist_L.s";
connectAttr "rig:Wrist_L.s" "rig:IndexFinger1_L.is";
connectAttr "rig:IndexFinger1_L.s" "rig:IndexFinger2_L.is";
connectAttr "rig:IndexFinger2_L.s" "rig:IndexFinger3_L.is";
connectAttr "rig:IndexFinger3_L.s" "rig:IndexFinger4_L.is";
connectAttr "rig:Wrist_L.s" "rig:MiddleFinger1_L.is";
connectAttr "rig:MiddleFinger1_L.s" "rig:MiddleFinger2_L.is";
connectAttr "rig:MiddleFinger2_L.s" "rig:MiddleFinger3_L.is";
connectAttr "rig:MiddleFinger3_L.s" "rig:MiddleFinger4_L.is";
connectAttr "rig:Wrist_L.s" "rig:Cup_L.is";
connectAttr "rig:Cup_L.s" "rig:PinkyFinger1_L.is";
connectAttr "rig:PinkyFinger1_L.s" "rig:PinkyFinger2_L.is";
connectAttr "rig:PinkyFinger2_L.s" "rig:PinkyFinger3_L.is";
connectAttr "rig:PinkyFinger3_L.s" "rig:PinkyFinger4_L.is";
connectAttr "rig:Cup_L.s" "rig:RingFinger1_L.is";
connectAttr "rig:RingFinger1_L.s" "rig:RingFinger2_L.is";
connectAttr "rig:RingFinger2_L.s" "rig:RingFinger3_L.is";
connectAttr "rig:RingFinger3_L.s" "rig:RingFinger4_L.is";
connectAttr "rig:Wrist_L.s" "rig:ThumbFinger1_L.is";
connectAttr "rig:ThumbFinger1_L.s" "rig:ThumbFinger2_L.is";
connectAttr "rig:ThumbFinger2_L.s" "rig:ThumbFinger3_L.is";
connectAttr "rig:ThumbFinger3_L.s" "rig:ThumbFinger4_L.is";
connectAttr "rig:Spine2_M.s" "rig:Breast_R.is";
connectAttr "rig:Breast_R.s" "rig:BreastEnd_R.is";
connectAttr "rig:FKBreast_L.s" "rig:Breast_L.s";
connectAttr "rig:Spine2_M.s" "rig:Breast_L.is";
connectAttr "rig:Breast_L_parentConstraint1.ctx" "rig:Breast_L.tx";
connectAttr "rig:Breast_L_parentConstraint1.cty" "rig:Breast_L.ty";
connectAttr "rig:Breast_L_parentConstraint1.ctz" "rig:Breast_L.tz";
connectAttr "rig:Breast_L_parentConstraint1.crx" "rig:Breast_L.rx";
connectAttr "rig:Breast_L_parentConstraint1.cry" "rig:Breast_L.ry";
connectAttr "rig:Breast_L_parentConstraint1.crz" "rig:Breast_L.rz";
connectAttr "rig:Breast_L.s" "rig:BreastEnd_L.is";
connectAttr "rig:Hip_L_pointConstraint1.ctx" "rig:Hip_L.tx";
connectAttr "rig:Hip_L_pointConstraint1.cty" "rig:Hip_L.ty";
connectAttr "rig:Hip_L_pointConstraint1.ctz" "rig:Hip_L.tz";
connectAttr "rig:Hip_L_orientConstraint1.crx" "rig:Hip_L.rx";
connectAttr "rig:Hip_L_orientConstraint1.cry" "rig:Hip_L.ry";
connectAttr "rig:Hip_L_orientConstraint1.crz" "rig:Hip_L.rz";
connectAttr "rig:ScaleBlendHip_L.op" "rig:Hip_L.s";
connectAttr "rig:Root_M.s" "rig:Hip_L.is";
connectAttr "rig:Hip_L.s" "rig:HipPart1_L.is";
connectAttr "rig:Hip_L.sx" "rig:HipPart1_L.sx";
connectAttr "rig:Hip_L.sy" "rig:HipPart1_L.sy";
connectAttr "rig:Hip_L.sz" "rig:HipPart1_L.sz";
connectAttr "rig:HipPart1_L_orientConstraint1.crx" "rig:HipPart1_L.rx";
connectAttr "rig:HipPart1_L_orientConstraint1.cry" "rig:HipPart1_L.ry";
connectAttr "rig:HipPart1_L_orientConstraint1.crz" "rig:HipPart1_L.rz";
connectAttr "rig:HipPart1_L_pointConstraint1.ctx" "rig:HipPart1_L.tx";
connectAttr "rig:HipPart1_L_pointConstraint1.cty" "rig:HipPart1_L.ty";
connectAttr "rig:HipPart1_L_pointConstraint1.ctz" "rig:HipPart1_L.tz";
connectAttr "rig:HipPart1_L.s" "rig:HipPart2_L.is";
connectAttr "rig:Hip_L.sx" "rig:HipPart2_L.sx";
connectAttr "rig:Hip_L.sy" "rig:HipPart2_L.sy";
connectAttr "rig:Hip_L.sz" "rig:HipPart2_L.sz";
connectAttr "rig:HipPart2_L_orientConstraint1.crx" "rig:HipPart2_L.rx";
connectAttr "rig:HipPart2_L_orientConstraint1.cry" "rig:HipPart2_L.ry";
connectAttr "rig:HipPart2_L_orientConstraint1.crz" "rig:HipPart2_L.rz";
connectAttr "rig:HipPart2_L_pointConstraint1.ctx" "rig:HipPart2_L.tx";
connectAttr "rig:HipPart2_L_pointConstraint1.cty" "rig:HipPart2_L.ty";
connectAttr "rig:HipPart2_L_pointConstraint1.ctz" "rig:HipPart2_L.tz";
connectAttr "rig:ScaleBlendKnee_L.op" "rig:Knee_L.s";
connectAttr "rig:Knee_L_parentConstraint1.ctx" "rig:Knee_L.tx";
connectAttr "rig:Knee_L_parentConstraint1.cty" "rig:Knee_L.ty";
connectAttr "rig:Knee_L_parentConstraint1.ctz" "rig:Knee_L.tz";
connectAttr "rig:Knee_L_parentConstraint1.crx" "rig:Knee_L.rx";
connectAttr "rig:Knee_L_parentConstraint1.cry" "rig:Knee_L.ry";
connectAttr "rig:Knee_L_parentConstraint1.crz" "rig:Knee_L.rz";
connectAttr "rig:Ankle_L_parentConstraint1.ctx" "rig:Ankle_L.tx";
connectAttr "rig:Ankle_L_parentConstraint1.cty" "rig:Ankle_L.ty";
connectAttr "rig:Ankle_L_parentConstraint1.ctz" "rig:Ankle_L.tz";
connectAttr "rig:Ankle_L_parentConstraint1.crx" "rig:Ankle_L.rx";
connectAttr "rig:Ankle_L_parentConstraint1.cry" "rig:Ankle_L.ry";
connectAttr "rig:Ankle_L_parentConstraint1.crz" "rig:Ankle_L.rz";
connectAttr "rig:ScaleBlendAnkle_L.op" "rig:Ankle_L.s";
connectAttr "rig:Knee_L.s" "rig:Ankle_L.is";
connectAttr "rig:Ankle_L.s" "rig:Toes_L.is";
connectAttr "rig:Toes_L.s" "rig:ToesEnd_L.is";
connectAttr "rig:Hip_L.s" "rig:HipFat1_L.is";
connectAttr "rig:HipFat1_L.s" "rig:HipFatEnd_L.is";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "markerGroup1.depth" "mmMarkerScale1.dpt";
connectAttr "markerGroup1.overscan" "mmMarkerScale1.ovrscn";
connectAttr "perspShape2.fl" "mmMarkerScale1.fl";
connectAttr "perspShape2.cap" "mmMarkerScale1.cap";
connectAttr "perspShape2.fio" "mmMarkerScale1.fio";
connectAttr "rig:renderLayerManager.rlmi[0]" "rig:defaultRenderLayer.rlid";
connectAttr "rig:Group.msg" "rig:bindPose23.m[0]";
connectAttr "rig:Main.msg" "rig:bindPose23.m[1]";
connectAttr "rig:DeformationSystem.msg" "rig:bindPose23.m[2]";
connectAttr "rig:Root_M.msg" "rig:bindPose23.m[3]";
connectAttr "rig:Hip_R.msg" "rig:bindPose23.m[4]";
connectAttr "rig:HipPart1_R.msg" "rig:bindPose23.m[5]";
connectAttr "rig:HipPart2_R.msg" "rig:bindPose23.m[6]";
connectAttr "rig:Knee_R.msg" "rig:bindPose23.m[7]";
connectAttr "rig:Ankle_R.msg" "rig:bindPose23.m[8]";
connectAttr "rig:Toes_R.msg" "rig:bindPose23.m[9]";
connectAttr "rig:Hip_L.msg" "rig:bindPose23.m[10]";
connectAttr "rig:HipFat1_L.msg" "rig:bindPose23.m[11]";
connectAttr "rig:Spine1_M.msg" "rig:bindPose23.m[14]";
connectAttr "rig:Spine2_M.msg" "rig:bindPose23.m[15]";
connectAttr "rig:HipFat1_R.msg" "rig:bindPose23.m[16]";
connectAttr "rig:Chest_M.msg" "rig:bindPose23.m[17]";
connectAttr "rig:Scapula_R.msg" "rig:bindPose23.m[18]";
connectAttr "rig:Shoulder_R.msg" "rig:bindPose23.m[19]";
connectAttr "rig:ShoulderPart1_R.msg" "rig:bindPose23.m[20]";
connectAttr "rig:ShoulderPart2_R.msg" "rig:bindPose23.m[21]";
connectAttr "rig:Elbow_R.msg" "rig:bindPose23.m[22]";
connectAttr "rig:ElbowPart1_R.msg" "rig:bindPose23.m[23]";
connectAttr "rig:ElbowPart2_R.msg" "rig:bindPose23.m[24]";
connectAttr "rig:Wrist_R.msg" "rig:bindPose23.m[25]";
connectAttr "rig:MiddleFinger1_R.msg" "rig:bindPose23.m[26]";
connectAttr "rig:MiddleFinger2_R.msg" "rig:bindPose23.m[27]";
connectAttr "rig:IndexFinger1_R.msg" "rig:bindPose23.m[28]";
connectAttr "rig:IndexFinger2_R.msg" "rig:bindPose23.m[29]";
connectAttr "rig:IndexFinger3_R.msg" "rig:bindPose23.m[30]";
connectAttr "rig:Neck_M.msg" "rig:bindPose23.m[31]";
connectAttr "rig:NeckPart1_M.msg" "rig:bindPose23.m[32]";
connectAttr "rig:NeckPart2_M.msg" "rig:bindPose23.m[33]";
connectAttr "rig:Neck1_M.msg" "rig:bindPose23.m[34]";
connectAttr "rig:Neck2_M.msg" "rig:bindPose23.m[35]";
connectAttr "rig:Head_M.msg" "rig:bindPose23.m[36]";
connectAttr "rig:Scapula_L.msg" "rig:bindPose23.m[37]";
connectAttr "rig:Shoulder_L.msg" "rig:bindPose23.m[38]";
connectAttr "rig:ShoulderPart1_L.msg" "rig:bindPose23.m[39]";
connectAttr "rig:ShoulderPart2_L.msg" "rig:bindPose23.m[40]";
connectAttr "rig:Elbow_L.msg" "rig:bindPose23.m[41]";
connectAttr "rig:ElbowPart1_L.msg" "rig:bindPose23.m[42]";
connectAttr "rig:ElbowPart2_L.msg" "rig:bindPose23.m[43]";
connectAttr "rig:Wrist_L.msg" "rig:bindPose23.m[44]";
connectAttr "rig:IndexFinger1_L.msg" "rig:bindPose23.m[45]";
connectAttr "rig:ThumbFinger1_R.msg" "rig:bindPose23.m[46]";
connectAttr "rig:ThumbFinger2_R.msg" "rig:bindPose23.m[47]";
connectAttr "rig:ThumbFinger3_R.msg" "rig:bindPose23.m[48]";
connectAttr "rig:IndexFinger2_L.msg" "rig:bindPose23.m[49]";
connectAttr "rig:IndexFinger3_L.msg" "rig:bindPose23.m[50]";
connectAttr "rig:MiddleFinger1_L.msg" "rig:bindPose23.m[51]";
connectAttr "rig:MiddleFinger2_L.msg" "rig:bindPose23.m[52]";
connectAttr "rig:MiddleFinger3_L.msg" "rig:bindPose23.m[53]";
connectAttr "rig:Cup_L.msg" "rig:bindPose23.m[54]";
connectAttr "rig:PinkyFinger1_L.msg" "rig:bindPose23.m[55]";
connectAttr "rig:PinkyFinger2_L.msg" "rig:bindPose23.m[56]";
connectAttr "rig:PinkyFinger3_L.msg" "rig:bindPose23.m[57]";
connectAttr "rig:RingFinger1_L.msg" "rig:bindPose23.m[58]";
connectAttr "rig:RingFinger2_L.msg" "rig:bindPose23.m[59]";
connectAttr "rig:RingFinger3_L.msg" "rig:bindPose23.m[60]";
connectAttr "rig:ThumbFinger1_L.msg" "rig:bindPose23.m[61]";
connectAttr "rig:ThumbFinger2_L.msg" "rig:bindPose23.m[62]";
connectAttr "rig:ThumbFinger3_L.msg" "rig:bindPose23.m[63]";
connectAttr "rig:Breast_R.msg" "rig:bindPose23.m[64]";
connectAttr "rig:Breast_L.msg" "rig:bindPose23.m[65]";
connectAttr "rig:HipPart1_L.msg" "rig:bindPose23.m[66]";
connectAttr "rig:HipPart2_L.msg" "rig:bindPose23.m[67]";
connectAttr "rig:Knee_L.msg" "rig:bindPose23.m[68]";
connectAttr "rig:Ankle_L.msg" "rig:bindPose23.m[69]";
connectAttr "rig:Toes_L.msg" "rig:bindPose23.m[70]";
connectAttr "rig:Cup_R.msg" "rig:bindPose23.m[71]";
connectAttr "rig:RingFinger1_R.msg" "rig:bindPose23.m[72]";
connectAttr "rig:MiddleFinger3_R.msg" "rig:bindPose23.m[73]";
connectAttr "rig:PinkyFinger1_R.msg" "rig:bindPose23.m[74]";
connectAttr "rig:PinkyFinger2_R.msg" "rig:bindPose23.m[75]";
connectAttr "rig:PinkyFinger3_R.msg" "rig:bindPose23.m[76]";
connectAttr "rig:RingFinger2_R.msg" "rig:bindPose23.m[77]";
connectAttr "rig:RingFinger3_R.msg" "rig:bindPose23.m[78]";
connectAttr "rig:RootPart1_M.msg" "rig:bindPose23.m[79]";
connectAttr "rig:RootPart2_M.msg" "rig:bindPose23.m[80]";
connectAttr "rig:bindPose23.w" "rig:bindPose23.p[0]";
connectAttr "rig:bindPose23.m[0]" "rig:bindPose23.p[1]";
connectAttr "rig:bindPose23.m[1]" "rig:bindPose23.p[2]";
connectAttr "rig:bindPose23.m[2]" "rig:bindPose23.p[3]";
connectAttr "rig:bindPose23.m[3]" "rig:bindPose23.p[4]";
connectAttr "rig:bindPose23.m[4]" "rig:bindPose23.p[5]";
connectAttr "rig:bindPose23.m[5]" "rig:bindPose23.p[6]";
connectAttr "rig:bindPose23.m[6]" "rig:bindPose23.p[7]";
connectAttr "rig:bindPose23.m[7]" "rig:bindPose23.p[8]";
connectAttr "rig:bindPose23.m[8]" "rig:bindPose23.p[9]";
connectAttr "rig:bindPose23.m[3]" "rig:bindPose23.p[10]";
connectAttr "rig:Hip_L.msg" "rig:bindPose23.p[11]";
connectAttr "rig:bindPose23.m[80]" "rig:bindPose23.p[14]";
connectAttr "rig:Spine1_M.msg" "rig:bindPose23.p[15]";
connectAttr "rig:bindPose23.m[4]" "rig:bindPose23.p[16]";
connectAttr "rig:bindPose23.m[15]" "rig:bindPose23.p[17]";
connectAttr "rig:Chest_M.msg" "rig:bindPose23.p[18]";
connectAttr "rig:Scapula_R.msg" "rig:bindPose23.p[19]";
connectAttr "rig:Shoulder_R.msg" "rig:bindPose23.p[20]";
connectAttr "rig:ShoulderPart1_R.msg" "rig:bindPose23.p[21]";
connectAttr "rig:ShoulderPart2_R.msg" "rig:bindPose23.p[22]";
connectAttr "rig:Elbow_R.msg" "rig:bindPose23.p[23]";
connectAttr "rig:ElbowPart1_R.msg" "rig:bindPose23.p[24]";
connectAttr "rig:ElbowPart2_R.msg" "rig:bindPose23.p[25]";
connectAttr "rig:Wrist_R.msg" "rig:bindPose23.p[26]";
connectAttr "rig:MiddleFinger1_R.msg" "rig:bindPose23.p[27]";
connectAttr "rig:bindPose23.m[25]" "rig:bindPose23.p[28]";
connectAttr "rig:IndexFinger1_R.msg" "rig:bindPose23.p[29]";
connectAttr "rig:IndexFinger2_R.msg" "rig:bindPose23.p[30]";
connectAttr "rig:bindPose23.m[17]" "rig:bindPose23.p[31]";
connectAttr "rig:Neck_M.msg" "rig:bindPose23.p[32]";
connectAttr "rig:NeckPart1_M.msg" "rig:bindPose23.p[33]";
connectAttr "rig:NeckPart2_M.msg" "rig:bindPose23.p[34]";
connectAttr "rig:Neck1_M.msg" "rig:bindPose23.p[35]";
connectAttr "rig:Neck2_M.msg" "rig:bindPose23.p[36]";
connectAttr "rig:bindPose23.m[17]" "rig:bindPose23.p[37]";
connectAttr "rig:Scapula_L.msg" "rig:bindPose23.p[38]";
connectAttr "rig:Shoulder_L.msg" "rig:bindPose23.p[39]";
connectAttr "rig:ShoulderPart1_L.msg" "rig:bindPose23.p[40]";
connectAttr "rig:ShoulderPart2_L.msg" "rig:bindPose23.p[41]";
connectAttr "rig:Elbow_L.msg" "rig:bindPose23.p[42]";
connectAttr "rig:ElbowPart1_L.msg" "rig:bindPose23.p[43]";
connectAttr "rig:ElbowPart2_L.msg" "rig:bindPose23.p[44]";
connectAttr "rig:Wrist_L.msg" "rig:bindPose23.p[45]";
connectAttr "rig:bindPose23.m[25]" "rig:bindPose23.p[46]";
connectAttr "rig:ThumbFinger1_R.msg" "rig:bindPose23.p[47]";
connectAttr "rig:ThumbFinger2_R.msg" "rig:bindPose23.p[48]";
connectAttr "rig:bindPose23.m[45]" "rig:bindPose23.p[49]";
connectAttr "rig:IndexFinger2_L.msg" "rig:bindPose23.p[50]";
connectAttr "rig:bindPose23.m[44]" "rig:bindPose23.p[51]";
connectAttr "rig:MiddleFinger1_L.msg" "rig:bindPose23.p[52]";
connectAttr "rig:MiddleFinger2_L.msg" "rig:bindPose23.p[53]";
connectAttr "rig:bindPose23.m[44]" "rig:bindPose23.p[54]";
connectAttr "rig:Cup_L.msg" "rig:bindPose23.p[55]";
connectAttr "rig:PinkyFinger1_L.msg" "rig:bindPose23.p[56]";
connectAttr "rig:PinkyFinger2_L.msg" "rig:bindPose23.p[57]";
connectAttr "rig:bindPose23.m[54]" "rig:bindPose23.p[58]";
connectAttr "rig:RingFinger1_L.msg" "rig:bindPose23.p[59]";
connectAttr "rig:RingFinger2_L.msg" "rig:bindPose23.p[60]";
connectAttr "rig:bindPose23.m[44]" "rig:bindPose23.p[61]";
connectAttr "rig:ThumbFinger1_L.msg" "rig:bindPose23.p[62]";
connectAttr "rig:ThumbFinger2_L.msg" "rig:bindPose23.p[63]";
connectAttr "rig:bindPose23.m[15]" "rig:bindPose23.p[64]";
connectAttr "rig:bindPose23.m[15]" "rig:bindPose23.p[65]";
connectAttr "rig:bindPose23.m[10]" "rig:bindPose23.p[66]";
connectAttr "rig:HipPart1_L.msg" "rig:bindPose23.p[67]";
connectAttr "rig:HipPart2_L.msg" "rig:bindPose23.p[68]";
connectAttr "rig:Knee_L.msg" "rig:bindPose23.p[69]";
connectAttr "rig:Ankle_L.msg" "rig:bindPose23.p[70]";
connectAttr "rig:bindPose23.m[25]" "rig:bindPose23.p[71]";
connectAttr "rig:Cup_R.msg" "rig:bindPose23.p[72]";
connectAttr "rig:bindPose23.m[27]" "rig:bindPose23.p[73]";
connectAttr "rig:bindPose23.m[71]" "rig:bindPose23.p[74]";
connectAttr "rig:PinkyFinger1_R.msg" "rig:bindPose23.p[75]";
connectAttr "rig:PinkyFinger2_R.msg" "rig:bindPose23.p[76]";
connectAttr "rig:bindPose23.m[72]" "rig:bindPose23.p[77]";
connectAttr "rig:RingFinger2_R.msg" "rig:bindPose23.p[78]";
connectAttr "rig:bindPose23.m[3]" "rig:bindPose23.p[79]";
connectAttr "rig:RootPart1_M.msg" "rig:bindPose23.p[80]";
connectAttr "rig:bindPose23.m[0]" "rig:bindPose23.p[81]";
connectAttr "rig:bindPose23.m[83]" "rig:bindPose23.p[85]";
connectAttr "rig:bindPose23.m[83]" "rig:bindPose23.p[86]";
connectAttr "rig:bindPose23.m[83]" "rig:bindPose23.p[87]";
connectAttr "rig:bindPose23.m[82]" "rig:bindPose23.p[88]";
connectAttr "rig:bindPose23.m[89]" "rig:bindPose23.p[90]";
connectAttr "rig:bindPose23.m[88]" "rig:bindPose23.p[91]";
connectAttr "rig:bindPose23.m[83]" "rig:bindPose23.p[92]";
connectAttr "rig:bindPose23.m[83]" "rig:bindPose23.p[93]";
connectAttr "rig:bindPose23.m[83]" "rig:bindPose23.p[94]";
connectAttr "rig:bindPose23.m[83]" "rig:bindPose23.p[98]";
connectAttr "rig:bindPose23.m[83]" "rig:bindPose23.p[100]";
connectAttr "rig:bindPose23.m[83]" "rig:bindPose23.p[102]";
connectAttr "rig:bindPose23.m[83]" "rig:bindPose23.p[104]";
connectAttr "rig:bindPose23.m[83]" "rig:bindPose23.p[106]";
connectAttr "rig:bindPose23.m[83]" "rig:bindPose23.p[108]";
connectAttr "rig:bindPose23.m[88]" "rig:bindPose23.p[110]";
connectAttr "rig:bindPose23.m[88]" "rig:bindPose23.p[111]";
connectAttr "rig:Root_M.bps" "rig:bindPose23.wm[3]";
connectAttr "rig:Hip_R.bps" "rig:bindPose23.wm[4]";
connectAttr "rig:HipPart1_R.bps" "rig:bindPose23.wm[5]";
connectAttr "rig:HipPart2_R.bps" "rig:bindPose23.wm[6]";
connectAttr "rig:Knee_R.bps" "rig:bindPose23.wm[7]";
connectAttr "rig:Ankle_R.bps" "rig:bindPose23.wm[8]";
connectAttr "rig:Toes_R.bps" "rig:bindPose23.wm[9]";
connectAttr "rig:Hip_L.bps" "rig:bindPose23.wm[10]";
connectAttr "rig:HipFat1_L.bps" "rig:bindPose23.wm[11]";
connectAttr "rig:Spine1_M.bps" "rig:bindPose23.wm[14]";
connectAttr "rig:Spine2_M.bps" "rig:bindPose23.wm[15]";
connectAttr "rig:HipFat1_R.bps" "rig:bindPose23.wm[16]";
connectAttr "rig:Chest_M.bps" "rig:bindPose23.wm[17]";
connectAttr "rig:Scapula_R.bps" "rig:bindPose23.wm[18]";
connectAttr "rig:Shoulder_R.bps" "rig:bindPose23.wm[19]";
connectAttr "rig:ShoulderPart1_R.bps" "rig:bindPose23.wm[20]";
connectAttr "rig:ShoulderPart2_R.bps" "rig:bindPose23.wm[21]";
connectAttr "rig:Elbow_R.bps" "rig:bindPose23.wm[22]";
connectAttr "rig:ElbowPart1_R.bps" "rig:bindPose23.wm[23]";
connectAttr "rig:ElbowPart2_R.bps" "rig:bindPose23.wm[24]";
connectAttr "rig:Wrist_R.bps" "rig:bindPose23.wm[25]";
connectAttr "rig:MiddleFinger1_R.bps" "rig:bindPose23.wm[26]";
connectAttr "rig:MiddleFinger2_R.bps" "rig:bindPose23.wm[27]";
connectAttr "rig:IndexFinger1_R.bps" "rig:bindPose23.wm[28]";
connectAttr "rig:IndexFinger2_R.bps" "rig:bindPose23.wm[29]";
connectAttr "rig:IndexFinger3_R.bps" "rig:bindPose23.wm[30]";
connectAttr "rig:Neck_M.bps" "rig:bindPose23.wm[31]";
connectAttr "rig:NeckPart1_M.bps" "rig:bindPose23.wm[32]";
connectAttr "rig:NeckPart2_M.bps" "rig:bindPose23.wm[33]";
connectAttr "rig:Neck1_M.bps" "rig:bindPose23.wm[34]";
connectAttr "rig:Neck2_M.bps" "rig:bindPose23.wm[35]";
connectAttr "rig:Head_M.bps" "rig:bindPose23.wm[36]";
connectAttr "rig:Scapula_L.bps" "rig:bindPose23.wm[37]";
connectAttr "rig:Shoulder_L.bps" "rig:bindPose23.wm[38]";
connectAttr "rig:ShoulderPart1_L.bps" "rig:bindPose23.wm[39]";
connectAttr "rig:ShoulderPart2_L.bps" "rig:bindPose23.wm[40]";
connectAttr "rig:Elbow_L.bps" "rig:bindPose23.wm[41]";
connectAttr "rig:ElbowPart1_L.bps" "rig:bindPose23.wm[42]";
connectAttr "rig:ElbowPart2_L.bps" "rig:bindPose23.wm[43]";
connectAttr "rig:Wrist_L.bps" "rig:bindPose23.wm[44]";
connectAttr "rig:IndexFinger1_L.bps" "rig:bindPose23.wm[45]";
connectAttr "rig:ThumbFinger1_R.bps" "rig:bindPose23.wm[46]";
connectAttr "rig:ThumbFinger2_R.bps" "rig:bindPose23.wm[47]";
connectAttr "rig:ThumbFinger3_R.bps" "rig:bindPose23.wm[48]";
connectAttr "rig:IndexFinger2_L.bps" "rig:bindPose23.wm[49]";
connectAttr "rig:IndexFinger3_L.bps" "rig:bindPose23.wm[50]";
connectAttr "rig:MiddleFinger1_L.bps" "rig:bindPose23.wm[51]";
connectAttr "rig:MiddleFinger2_L.bps" "rig:bindPose23.wm[52]";
connectAttr "rig:MiddleFinger3_L.bps" "rig:bindPose23.wm[53]";
connectAttr "rig:Cup_L.bps" "rig:bindPose23.wm[54]";
connectAttr "rig:PinkyFinger1_L.bps" "rig:bindPose23.wm[55]";
connectAttr "rig:PinkyFinger2_L.bps" "rig:bindPose23.wm[56]";
connectAttr "rig:PinkyFinger3_L.bps" "rig:bindPose23.wm[57]";
connectAttr "rig:RingFinger1_L.bps" "rig:bindPose23.wm[58]";
connectAttr "rig:RingFinger2_L.bps" "rig:bindPose23.wm[59]";
connectAttr "rig:RingFinger3_L.bps" "rig:bindPose23.wm[60]";
connectAttr "rig:ThumbFinger1_L.bps" "rig:bindPose23.wm[61]";
connectAttr "rig:ThumbFinger2_L.bps" "rig:bindPose23.wm[62]";
connectAttr "rig:ThumbFinger3_L.bps" "rig:bindPose23.wm[63]";
connectAttr "rig:Breast_R.bps" "rig:bindPose23.wm[64]";
connectAttr "rig:Breast_L.bps" "rig:bindPose23.wm[65]";
connectAttr "rig:HipPart1_L.bps" "rig:bindPose23.wm[66]";
connectAttr "rig:HipPart2_L.bps" "rig:bindPose23.wm[67]";
connectAttr "rig:Knee_L.bps" "rig:bindPose23.wm[68]";
connectAttr "rig:Ankle_L.bps" "rig:bindPose23.wm[69]";
connectAttr "rig:Toes_L.bps" "rig:bindPose23.wm[70]";
connectAttr "rig:Cup_R.bps" "rig:bindPose23.wm[71]";
connectAttr "rig:RingFinger1_R.bps" "rig:bindPose23.wm[72]";
connectAttr "rig:MiddleFinger3_R.bps" "rig:bindPose23.wm[73]";
connectAttr "rig:PinkyFinger1_R.bps" "rig:bindPose23.wm[74]";
connectAttr "rig:PinkyFinger2_R.bps" "rig:bindPose23.wm[75]";
connectAttr "rig:PinkyFinger3_R.bps" "rig:bindPose23.wm[76]";
connectAttr "rig:RingFinger2_R.bps" "rig:bindPose23.wm[77]";
connectAttr "rig:RingFinger3_R.bps" "rig:bindPose23.wm[78]";
connectAttr "rig:RootPart1_M.bps" "rig:bindPose23.wm[79]";
connectAttr "rig:RootPart2_M.bps" "rig:bindPose23.wm[80]";
connectAttr "rig:Group.msg" "rig:bindPose15.m[0]";
connectAttr "rig:Main.msg" "rig:bindPose15.m[1]";
connectAttr "rig:DeformationSystem.msg" "rig:bindPose15.m[2]";
connectAttr "rig:Root_M.msg" "rig:bindPose15.m[3]";
connectAttr "rig:RootPart1_M.msg" "rig:bindPose15.m[4]";
connectAttr "rig:RootPart2_M.msg" "rig:bindPose15.m[5]";
connectAttr "rig:Spine1_M.msg" "rig:bindPose15.m[6]";
connectAttr "rig:Spine2_M.msg" "rig:bindPose15.m[7]";
connectAttr "rig:Chest_M.msg" "rig:bindPose15.m[8]";
connectAttr "rig:Scapula_R.msg" "rig:bindPose15.m[9]";
connectAttr "rig:Shoulder_R.msg" "rig:bindPose15.m[10]";
connectAttr "rig:ShoulderPart1_R.msg" "rig:bindPose15.m[11]";
connectAttr "rig:ShoulderPart2_R.msg" "rig:bindPose15.m[12]";
connectAttr "rig:Elbow_R.msg" "rig:bindPose15.m[13]";
connectAttr "rig:ElbowPart1_R.msg" "rig:bindPose15.m[14]";
connectAttr "rig:ElbowPart2_R.msg" "rig:bindPose15.m[15]";
connectAttr "rig:Wrist_R.msg" "rig:bindPose15.m[16]";
connectAttr "rig:MiddleFinger1_R.msg" "rig:bindPose15.m[17]";
connectAttr "rig:MiddleFinger2_R.msg" "rig:bindPose15.m[18]";
connectAttr "rig:MiddleFinger3_R.msg" "rig:bindPose15.m[19]";
connectAttr "rig:IndexFinger1_R.msg" "rig:bindPose15.m[20]";
connectAttr "rig:IndexFinger2_R.msg" "rig:bindPose15.m[21]";
connectAttr "rig:IndexFinger3_R.msg" "rig:bindPose15.m[22]";
connectAttr "rig:ThumbFinger1_R.msg" "rig:bindPose15.m[23]";
connectAttr "rig:Cup_R.msg" "rig:bindPose15.m[24]";
connectAttr "rig:Neck_M.msg" "rig:bindPose15.m[25]";
connectAttr "rig:NeckPart1_M.msg" "rig:bindPose15.m[26]";
connectAttr "rig:NeckPart2_M.msg" "rig:bindPose15.m[27]";
connectAttr "rig:Neck1_M.msg" "rig:bindPose15.m[28]";
connectAttr "rig:Neck2_M.msg" "rig:bindPose15.m[29]";
connectAttr "rig:Head_M.msg" "rig:bindPose15.m[30]";
connectAttr "rig:Breast_R.msg" "rig:bindPose15.m[31]";
connectAttr "rig:Breast_L.msg" "rig:bindPose15.m[32]";
connectAttr "rig:Hip_L.msg" "rig:bindPose15.m[33]";
connectAttr "rig:HipPart1_L.msg" "rig:bindPose15.m[34]";
connectAttr "rig:HipPart2_L.msg" "rig:bindPose15.m[35]";
connectAttr "rig:Knee_L.msg" "rig:bindPose15.m[36]";
connectAttr "rig:Ankle_L.msg" "rig:bindPose15.m[37]";
connectAttr "rig:Toes_L.msg" "rig:bindPose15.m[38]";
connectAttr "rig:Scapula_L.msg" "rig:bindPose15.m[39]";
connectAttr "rig:Hip_R.msg" "rig:bindPose15.m[40]";
connectAttr "rig:HipPart1_R.msg" "rig:bindPose15.m[41]";
connectAttr "rig:HipPart2_R.msg" "rig:bindPose15.m[42]";
connectAttr "rig:Knee_R.msg" "rig:bindPose15.m[43]";
connectAttr "rig:Ankle_R.msg" "rig:bindPose15.m[44]";
connectAttr "rig:Shoulder_L.msg" "rig:bindPose15.m[45]";
connectAttr "rig:ShoulderPart1_L.msg" "rig:bindPose15.m[46]";
connectAttr "rig:ShoulderPart2_L.msg" "rig:bindPose15.m[47]";
connectAttr "rig:Elbow_L.msg" "rig:bindPose15.m[48]";
connectAttr "rig:ElbowPart1_L.msg" "rig:bindPose15.m[49]";
connectAttr "rig:ElbowPart2_L.msg" "rig:bindPose15.m[50]";
connectAttr "rig:Wrist_L.msg" "rig:bindPose15.m[51]";
connectAttr "rig:IndexFinger1_L.msg" "rig:bindPose15.m[52]";
connectAttr "rig:IndexFinger2_L.msg" "rig:bindPose15.m[53]";
connectAttr "rig:IndexFinger3_L.msg" "rig:bindPose15.m[54]";
connectAttr "rig:MiddleFinger1_L.msg" "rig:bindPose15.m[55]";
connectAttr "rig:MiddleFinger2_L.msg" "rig:bindPose15.m[56]";
connectAttr "rig:MiddleFinger3_L.msg" "rig:bindPose15.m[57]";
connectAttr "rig:Cup_L.msg" "rig:bindPose15.m[58]";
connectAttr "rig:PinkyFinger1_L.msg" "rig:bindPose15.m[59]";
connectAttr "rig:PinkyFinger1_R.msg" "rig:bindPose15.m[60]";
connectAttr "rig:PinkyFinger2_L.msg" "rig:bindPose15.m[61]";
connectAttr "rig:PinkyFinger2_R.msg" "rig:bindPose15.m[62]";
connectAttr "rig:PinkyFinger3_L.msg" "rig:bindPose15.m[63]";
connectAttr "rig:PinkyFinger3_R.msg" "rig:bindPose15.m[64]";
connectAttr "rig:RingFinger1_L.msg" "rig:bindPose15.m[65]";
connectAttr "rig:RingFinger1_R.msg" "rig:bindPose15.m[66]";
connectAttr "rig:RingFinger2_L.msg" "rig:bindPose15.m[67]";
connectAttr "rig:RingFinger2_R.msg" "rig:bindPose15.m[68]";
connectAttr "rig:RingFinger3_L.msg" "rig:bindPose15.m[69]";
connectAttr "rig:RingFinger3_R.msg" "rig:bindPose15.m[70]";
connectAttr "rig:ThumbFinger1_L.msg" "rig:bindPose15.m[71]";
connectAttr "rig:ThumbFinger2_L.msg" "rig:bindPose15.m[72]";
connectAttr "rig:ThumbFinger2_R.msg" "rig:bindPose15.m[73]";
connectAttr "rig:ThumbFinger3_L.msg" "rig:bindPose15.m[74]";
connectAttr "rig:ThumbFinger3_R.msg" "rig:bindPose15.m[75]";
connectAttr "rig:Toes_R.msg" "rig:bindPose15.m[76]";
connectAttr "rig:HipFat1_L.msg" "rig:bindPose15.m[77]";
connectAttr "rig:HipFat1_R.msg" "rig:bindPose15.m[78]";
connectAttr "rig:bindPose15.w" "rig:bindPose15.p[0]";
connectAttr "rig:bindPose15.m[0]" "rig:bindPose15.p[1]";
connectAttr "rig:bindPose15.m[1]" "rig:bindPose15.p[2]";
connectAttr "rig:bindPose15.m[2]" "rig:bindPose15.p[3]";
connectAttr "rig:bindPose15.m[3]" "rig:bindPose15.p[4]";
connectAttr "rig:bindPose15.m[4]" "rig:bindPose15.p[5]";
connectAttr "rig:bindPose15.m[5]" "rig:bindPose15.p[6]";
connectAttr "rig:bindPose15.m[6]" "rig:bindPose15.p[7]";
connectAttr "rig:bindPose15.m[7]" "rig:bindPose15.p[8]";
connectAttr "rig:bindPose15.m[8]" "rig:bindPose15.p[9]";
connectAttr "rig:bindPose15.m[9]" "rig:bindPose15.p[10]";
connectAttr "rig:bindPose15.m[10]" "rig:bindPose15.p[11]";
connectAttr "rig:bindPose15.m[11]" "rig:bindPose15.p[12]";
connectAttr "rig:bindPose15.m[12]" "rig:bindPose15.p[13]";
connectAttr "rig:bindPose15.m[13]" "rig:bindPose15.p[14]";
connectAttr "rig:bindPose15.m[14]" "rig:bindPose15.p[15]";
connectAttr "rig:bindPose15.m[15]" "rig:bindPose15.p[16]";
connectAttr "rig:bindPose15.m[16]" "rig:bindPose15.p[17]";
connectAttr "rig:bindPose15.m[17]" "rig:bindPose15.p[18]";
connectAttr "rig:bindPose15.m[18]" "rig:bindPose15.p[19]";
connectAttr "rig:bindPose15.m[16]" "rig:bindPose15.p[20]";
connectAttr "rig:IndexFinger1_R.msg" "rig:bindPose15.p[21]";
connectAttr "rig:IndexFinger2_R.msg" "rig:bindPose15.p[22]";
connectAttr "rig:bindPose15.m[16]" "rig:bindPose15.p[23]";
connectAttr "rig:bindPose15.m[16]" "rig:bindPose15.p[24]";
connectAttr "rig:bindPose15.m[8]" "rig:bindPose15.p[25]";
connectAttr "rig:Neck_M.msg" "rig:bindPose15.p[26]";
connectAttr "rig:NeckPart1_M.msg" "rig:bindPose15.p[27]";
connectAttr "rig:NeckPart2_M.msg" "rig:bindPose15.p[28]";
connectAttr "rig:Neck1_M.msg" "rig:bindPose15.p[29]";
connectAttr "rig:Neck2_M.msg" "rig:bindPose15.p[30]";
connectAttr "rig:bindPose15.m[7]" "rig:bindPose15.p[31]";
connectAttr "rig:bindPose15.m[7]" "rig:bindPose15.p[32]";
connectAttr "rig:bindPose15.m[3]" "rig:bindPose15.p[33]";
connectAttr "rig:Hip_L.msg" "rig:bindPose15.p[34]";
connectAttr "rig:HipPart1_L.msg" "rig:bindPose15.p[35]";
connectAttr "rig:HipPart2_L.msg" "rig:bindPose15.p[36]";
connectAttr "rig:Knee_L.msg" "rig:bindPose15.p[37]";
connectAttr "rig:Ankle_L.msg" "rig:bindPose15.p[38]";
connectAttr "rig:bindPose15.m[8]" "rig:bindPose15.p[39]";
connectAttr "rig:bindPose15.m[3]" "rig:bindPose15.p[40]";
connectAttr "rig:Hip_R.msg" "rig:bindPose15.p[41]";
connectAttr "rig:HipPart1_R.msg" "rig:bindPose15.p[42]";
connectAttr "rig:HipPart2_R.msg" "rig:bindPose15.p[43]";
connectAttr "rig:Knee_R.msg" "rig:bindPose15.p[44]";
connectAttr "rig:bindPose15.m[39]" "rig:bindPose15.p[45]";
connectAttr "rig:Shoulder_L.msg" "rig:bindPose15.p[46]";
connectAttr "rig:ShoulderPart1_L.msg" "rig:bindPose15.p[47]";
connectAttr "rig:ShoulderPart2_L.msg" "rig:bindPose15.p[48]";
connectAttr "rig:Elbow_L.msg" "rig:bindPose15.p[49]";
connectAttr "rig:ElbowPart1_L.msg" "rig:bindPose15.p[50]";
connectAttr "rig:bindPose15.m[50]" "rig:bindPose15.p[51]";
connectAttr "rig:bindPose15.m[51]" "rig:bindPose15.p[52]";
connectAttr "rig:bindPose15.m[52]" "rig:bindPose15.p[53]";
connectAttr "rig:bindPose15.m[53]" "rig:bindPose15.p[54]";
connectAttr "rig:bindPose15.m[51]" "rig:bindPose15.p[55]";
connectAttr "rig:bindPose15.m[55]" "rig:bindPose15.p[56]";
connectAttr "rig:bindPose15.m[56]" "rig:bindPose15.p[57]";
connectAttr "rig:bindPose15.m[51]" "rig:bindPose15.p[58]";
connectAttr "rig:Cup_L.msg" "rig:bindPose15.p[59]";
connectAttr "rig:bindPose15.m[24]" "rig:bindPose15.p[60]";
connectAttr "rig:bindPose15.m[59]" "rig:bindPose15.p[61]";
connectAttr "rig:bindPose15.m[60]" "rig:bindPose15.p[62]";
connectAttr "rig:bindPose15.m[61]" "rig:bindPose15.p[63]";
connectAttr "rig:bindPose15.m[62]" "rig:bindPose15.p[64]";
connectAttr "rig:bindPose15.m[58]" "rig:bindPose15.p[65]";
connectAttr "rig:bindPose15.m[24]" "rig:bindPose15.p[66]";
connectAttr "rig:bindPose15.m[65]" "rig:bindPose15.p[67]";
connectAttr "rig:bindPose15.m[66]" "rig:bindPose15.p[68]";
connectAttr "rig:bindPose15.m[67]" "rig:bindPose15.p[69]";
connectAttr "rig:bindPose15.m[68]" "rig:bindPose15.p[70]";
connectAttr "rig:bindPose15.m[51]" "rig:bindPose15.p[71]";
connectAttr "rig:ThumbFinger1_L.msg" "rig:bindPose15.p[72]";
connectAttr "rig:bindPose15.m[23]" "rig:bindPose15.p[73]";
connectAttr "rig:bindPose15.m[72]" "rig:bindPose15.p[74]";
connectAttr "rig:bindPose15.m[73]" "rig:bindPose15.p[75]";
connectAttr "rig:bindPose15.m[44]" "rig:bindPose15.p[76]";
connectAttr "rig:bindPose15.m[33]" "rig:bindPose15.p[77]";
connectAttr "rig:bindPose15.m[40]" "rig:bindPose15.p[78]";
connectAttr "rig:bindPose15.m[30]" "rig:bindPose15.p[79]";
connectAttr "rig:bindPose15.m[79]" "rig:bindPose15.p[80]";
connectAttr "rig:IndexFinger1_R.bps" "rig:bindPose15.wm[20]";
connectAttr "rig:IndexFinger2_R.bps" "rig:bindPose15.wm[21]";
connectAttr "rig:IndexFinger3_R.bps" "rig:bindPose15.wm[22]";
connectAttr "rig:ThumbFinger1_R.bps" "rig:bindPose15.wm[23]";
connectAttr "rig:Cup_R.bps" "rig:bindPose15.wm[24]";
connectAttr "rig:Neck_M.bps" "rig:bindPose15.wm[25]";
connectAttr "rig:NeckPart1_M.bps" "rig:bindPose15.wm[26]";
connectAttr "rig:NeckPart2_M.bps" "rig:bindPose15.wm[27]";
connectAttr "rig:Neck1_M.bps" "rig:bindPose15.wm[28]";
connectAttr "rig:Neck2_M.bps" "rig:bindPose15.wm[29]";
connectAttr "rig:Head_M.bps" "rig:bindPose15.wm[30]";
connectAttr "rig:Breast_R.bps" "rig:bindPose15.wm[31]";
connectAttr "rig:Breast_L.bps" "rig:bindPose15.wm[32]";
connectAttr "rig:Hip_L.bps" "rig:bindPose15.wm[33]";
connectAttr "rig:HipPart1_L.bps" "rig:bindPose15.wm[34]";
connectAttr "rig:HipPart2_L.bps" "rig:bindPose15.wm[35]";
connectAttr "rig:Knee_L.bps" "rig:bindPose15.wm[36]";
connectAttr "rig:Ankle_L.bps" "rig:bindPose15.wm[37]";
connectAttr "rig:Toes_L.bps" "rig:bindPose15.wm[38]";
connectAttr "rig:Scapula_L.bps" "rig:bindPose15.wm[39]";
connectAttr "rig:Hip_R.bps" "rig:bindPose15.wm[40]";
connectAttr "rig:HipPart1_R.bps" "rig:bindPose15.wm[41]";
connectAttr "rig:HipPart2_R.bps" "rig:bindPose15.wm[42]";
connectAttr "rig:Knee_R.bps" "rig:bindPose15.wm[43]";
connectAttr "rig:Ankle_R.bps" "rig:bindPose15.wm[44]";
connectAttr "rig:Shoulder_L.bps" "rig:bindPose15.wm[45]";
connectAttr "rig:ShoulderPart1_L.bps" "rig:bindPose15.wm[46]";
connectAttr "rig:ShoulderPart2_L.bps" "rig:bindPose15.wm[47]";
connectAttr "rig:Elbow_L.bps" "rig:bindPose15.wm[48]";
connectAttr "rig:ElbowPart1_L.bps" "rig:bindPose15.wm[49]";
connectAttr "rig:ElbowPart2_L.bps" "rig:bindPose15.wm[50]";
connectAttr "rig:Wrist_L.bps" "rig:bindPose15.wm[51]";
connectAttr "rig:IndexFinger1_L.bps" "rig:bindPose15.wm[52]";
connectAttr "rig:IndexFinger2_L.bps" "rig:bindPose15.wm[53]";
connectAttr "rig:IndexFinger3_L.bps" "rig:bindPose15.wm[54]";
connectAttr "rig:MiddleFinger1_L.bps" "rig:bindPose15.wm[55]";
connectAttr "rig:MiddleFinger2_L.bps" "rig:bindPose15.wm[56]";
connectAttr "rig:MiddleFinger3_L.bps" "rig:bindPose15.wm[57]";
connectAttr "rig:Cup_L.bps" "rig:bindPose15.wm[58]";
connectAttr "rig:PinkyFinger1_L.bps" "rig:bindPose15.wm[59]";
connectAttr "rig:PinkyFinger1_R.bps" "rig:bindPose15.wm[60]";
connectAttr "rig:PinkyFinger2_L.bps" "rig:bindPose15.wm[61]";
connectAttr "rig:PinkyFinger2_R.bps" "rig:bindPose15.wm[62]";
connectAttr "rig:PinkyFinger3_L.bps" "rig:bindPose15.wm[63]";
connectAttr "rig:PinkyFinger3_R.bps" "rig:bindPose15.wm[64]";
connectAttr "rig:RingFinger1_L.bps" "rig:bindPose15.wm[65]";
connectAttr "rig:RingFinger1_R.bps" "rig:bindPose15.wm[66]";
connectAttr "rig:RingFinger2_L.bps" "rig:bindPose15.wm[67]";
connectAttr "rig:RingFinger2_R.bps" "rig:bindPose15.wm[68]";
connectAttr "rig:RingFinger3_L.bps" "rig:bindPose15.wm[69]";
connectAttr "rig:RingFinger3_R.bps" "rig:bindPose15.wm[70]";
connectAttr "rig:ThumbFinger1_L.bps" "rig:bindPose15.wm[71]";
connectAttr "rig:ThumbFinger2_L.bps" "rig:bindPose15.wm[72]";
connectAttr "rig:ThumbFinger2_R.bps" "rig:bindPose15.wm[73]";
connectAttr "rig:ThumbFinger3_L.bps" "rig:bindPose15.wm[74]";
connectAttr "rig:ThumbFinger3_R.bps" "rig:bindPose15.wm[75]";
connectAttr "rig:Toes_R.bps" "rig:bindPose15.wm[76]";
connectAttr "rig:HipFat1_L.bps" "rig:bindPose15.wm[77]";
connectAttr "rig:HipFat1_R.bps" "rig:bindPose15.wm[78]";
connectAttr "rig:Group.msg" "rig:bindPose3.m[0]";
connectAttr "rig:Main.msg" "rig:bindPose3.m[1]";
connectAttr "rig:DeformationSystem.msg" "rig:bindPose3.m[2]";
connectAttr "rig:Root_M.msg" "rig:bindPose3.m[3]";
connectAttr "rig:RootPart1_M.msg" "rig:bindPose3.m[4]";
connectAttr "rig:RootPart2_M.msg" "rig:bindPose3.m[5]";
connectAttr "rig:Spine1_M.msg" "rig:bindPose3.m[6]";
connectAttr "rig:Spine2_M.msg" "rig:bindPose3.m[7]";
connectAttr "rig:Chest_M.msg" "rig:bindPose3.m[8]";
connectAttr "rig:Scapula_R.msg" "rig:bindPose3.m[9]";
connectAttr "rig:Shoulder_R.msg" "rig:bindPose3.m[10]";
connectAttr "rig:ShoulderPart1_R.msg" "rig:bindPose3.m[11]";
connectAttr "rig:ShoulderPart2_R.msg" "rig:bindPose3.m[12]";
connectAttr "rig:Elbow_R.msg" "rig:bindPose3.m[13]";
connectAttr "rig:ElbowPart1_R.msg" "rig:bindPose3.m[14]";
connectAttr "rig:ElbowPart2_R.msg" "rig:bindPose3.m[15]";
connectAttr "rig:Wrist_R.msg" "rig:bindPose3.m[16]";
connectAttr "rig:ThumbFinger1_R.msg" "rig:bindPose3.m[17]";
connectAttr "rig:ThumbFinger2_R.msg" "rig:bindPose3.m[18]";
connectAttr "rig:ThumbFinger3_R.msg" "rig:bindPose3.m[19]";
connectAttr "rig:bindPose3.w" "rig:bindPose3.p[0]";
connectAttr "rig:bindPose3.m[0]" "rig:bindPose3.p[1]";
connectAttr "rig:bindPose3.m[1]" "rig:bindPose3.p[2]";
connectAttr "rig:bindPose3.m[2]" "rig:bindPose3.p[3]";
connectAttr "rig:bindPose3.m[3]" "rig:bindPose3.p[4]";
connectAttr "rig:bindPose3.m[4]" "rig:bindPose3.p[5]";
connectAttr "rig:bindPose3.m[5]" "rig:bindPose3.p[6]";
connectAttr "rig:bindPose3.m[6]" "rig:bindPose3.p[7]";
connectAttr "rig:bindPose3.m[7]" "rig:bindPose3.p[8]";
connectAttr "rig:bindPose3.m[8]" "rig:bindPose3.p[9]";
connectAttr "rig:bindPose3.m[9]" "rig:bindPose3.p[10]";
connectAttr "rig:bindPose3.m[10]" "rig:bindPose3.p[11]";
connectAttr "rig:bindPose3.m[11]" "rig:bindPose3.p[12]";
connectAttr "rig:bindPose3.m[12]" "rig:bindPose3.p[13]";
connectAttr "rig:bindPose3.m[13]" "rig:bindPose3.p[14]";
connectAttr "rig:bindPose3.m[14]" "rig:bindPose3.p[15]";
connectAttr "rig:bindPose3.m[15]" "rig:bindPose3.p[16]";
connectAttr "rig:bindPose3.m[16]" "rig:bindPose3.p[17]";
connectAttr "rig:bindPose3.m[17]" "rig:bindPose3.p[18]";
connectAttr "rig:bindPose3.m[18]" "rig:bindPose3.p[19]";
connectAttr "rig:Group.msg" "rig:bindPose5.m[0]";
connectAttr "rig:Main.msg" "rig:bindPose5.m[1]";
connectAttr "rig:DeformationSystem.msg" "rig:bindPose5.m[2]";
connectAttr "rig:Root_M.msg" "rig:bindPose5.m[3]";
connectAttr "rig:RootPart1_M.msg" "rig:bindPose5.m[4]";
connectAttr "rig:RootPart2_M.msg" "rig:bindPose5.m[5]";
connectAttr "rig:Spine1_M.msg" "rig:bindPose5.m[6]";
connectAttr "rig:Spine2_M.msg" "rig:bindPose5.m[7]";
connectAttr "rig:Chest_M.msg" "rig:bindPose5.m[8]";
connectAttr "rig:Scapula_R.msg" "rig:bindPose5.m[9]";
connectAttr "rig:Shoulder_R.msg" "rig:bindPose5.m[10]";
connectAttr "rig:ShoulderPart1_R.msg" "rig:bindPose5.m[11]";
connectAttr "rig:ShoulderPart2_R.msg" "rig:bindPose5.m[12]";
connectAttr "rig:Elbow_R.msg" "rig:bindPose5.m[13]";
connectAttr "rig:ElbowPart1_R.msg" "rig:bindPose5.m[14]";
connectAttr "rig:ElbowPart2_R.msg" "rig:bindPose5.m[15]";
connectAttr "rig:Wrist_R.msg" "rig:bindPose5.m[16]";
connectAttr "rig:Cup_R.msg" "rig:bindPose5.m[17]";
connectAttr "rig:PinkyFinger1_R.msg" "rig:bindPose5.m[18]";
connectAttr "rig:PinkyFinger2_R.msg" "rig:bindPose5.m[19]";
connectAttr "rig:PinkyFinger3_R.msg" "rig:bindPose5.m[20]";
connectAttr "rig:RingFinger1_R.msg" "rig:bindPose5.m[21]";
connectAttr "rig:RingFinger2_R.msg" "rig:bindPose5.m[22]";
connectAttr "rig:RingFinger3_R.msg" "rig:bindPose5.m[23]";
connectAttr "rig:bindPose5.w" "rig:bindPose5.p[0]";
connectAttr "rig:bindPose5.m[0]" "rig:bindPose5.p[1]";
connectAttr "rig:bindPose5.m[1]" "rig:bindPose5.p[2]";
connectAttr "rig:bindPose5.m[2]" "rig:bindPose5.p[3]";
connectAttr "rig:bindPose5.m[3]" "rig:bindPose5.p[4]";
connectAttr "rig:bindPose5.m[4]" "rig:bindPose5.p[5]";
connectAttr "rig:bindPose5.m[5]" "rig:bindPose5.p[6]";
connectAttr "rig:bindPose5.m[6]" "rig:bindPose5.p[7]";
connectAttr "rig:bindPose5.m[7]" "rig:bindPose5.p[8]";
connectAttr "rig:bindPose5.m[8]" "rig:bindPose5.p[9]";
connectAttr "rig:bindPose5.m[9]" "rig:bindPose5.p[10]";
connectAttr "rig:bindPose5.m[10]" "rig:bindPose5.p[11]";
connectAttr "rig:bindPose5.m[11]" "rig:bindPose5.p[12]";
connectAttr "rig:bindPose5.m[12]" "rig:bindPose5.p[13]";
connectAttr "rig:bindPose5.m[13]" "rig:bindPose5.p[14]";
connectAttr "rig:bindPose5.m[14]" "rig:bindPose5.p[15]";
connectAttr "rig:bindPose5.m[15]" "rig:bindPose5.p[16]";
connectAttr "rig:bindPose5.m[16]" "rig:bindPose5.p[17]";
connectAttr "rig:bindPose5.m[17]" "rig:bindPose5.p[18]";
connectAttr "rig:bindPose5.m[18]" "rig:bindPose5.p[19]";
connectAttr "rig:bindPose5.m[19]" "rig:bindPose5.p[20]";
connectAttr "rig:bindPose5.m[17]" "rig:bindPose5.p[21]";
connectAttr "rig:RingFinger1_R.msg" "rig:bindPose5.p[22]";
connectAttr "rig:RingFinger2_R.msg" "rig:bindPose5.p[23]";
connectAttr "rig:RingFinger1_R.bps" "rig:bindPose5.wm[21]";
connectAttr "rig:RingFinger2_R.bps" "rig:bindPose5.wm[22]";
connectAttr "rig:RingFinger3_R.bps" "rig:bindPose5.wm[23]";
connectAttr "rig:Group.msg" "rig:bindPose7.m[0]";
connectAttr "rig:Main.msg" "rig:bindPose7.m[1]";
connectAttr "rig:DeformationSystem.msg" "rig:bindPose7.m[2]";
connectAttr "rig:Root_M.msg" "rig:bindPose7.m[3]";
connectAttr "rig:RootPart1_M.msg" "rig:bindPose7.m[4]";
connectAttr "rig:RootPart2_M.msg" "rig:bindPose7.m[5]";
connectAttr "rig:Spine1_M.msg" "rig:bindPose7.m[6]";
connectAttr "rig:Spine2_M.msg" "rig:bindPose7.m[7]";
connectAttr "rig:Chest_M.msg" "rig:bindPose7.m[8]";
connectAttr "rig:Scapula_L.msg" "rig:bindPose7.m[9]";
connectAttr "rig:Shoulder_L.msg" "rig:bindPose7.m[10]";
connectAttr "rig:ShoulderPart1_L.msg" "rig:bindPose7.m[11]";
connectAttr "rig:ShoulderPart2_L.msg" "rig:bindPose7.m[12]";
connectAttr "rig:Elbow_L.msg" "rig:bindPose7.m[13]";
connectAttr "rig:ElbowPart1_L.msg" "rig:bindPose7.m[14]";
connectAttr "rig:ElbowPart2_L.msg" "rig:bindPose7.m[15]";
connectAttr "rig:Wrist_L.msg" "rig:bindPose7.m[16]";
connectAttr "rig:MiddleFinger1_L.msg" "rig:bindPose7.m[17]";
connectAttr "rig:MiddleFinger2_L.msg" "rig:bindPose7.m[18]";
connectAttr "rig:MiddleFinger3_L.msg" "rig:bindPose7.m[19]";
connectAttr "rig:bindPose7.w" "rig:bindPose7.p[0]";
connectAttr "rig:bindPose7.m[0]" "rig:bindPose7.p[1]";
connectAttr "rig:bindPose7.m[1]" "rig:bindPose7.p[2]";
connectAttr "rig:bindPose7.m[2]" "rig:bindPose7.p[3]";
connectAttr "rig:bindPose7.m[3]" "rig:bindPose7.p[4]";
connectAttr "rig:bindPose7.m[4]" "rig:bindPose7.p[5]";
connectAttr "rig:bindPose7.m[5]" "rig:bindPose7.p[6]";
connectAttr "rig:bindPose7.m[6]" "rig:bindPose7.p[7]";
connectAttr "rig:bindPose7.m[7]" "rig:bindPose7.p[8]";
connectAttr "rig:bindPose7.m[8]" "rig:bindPose7.p[9]";
connectAttr "rig:bindPose7.m[9]" "rig:bindPose7.p[10]";
connectAttr "rig:bindPose7.m[10]" "rig:bindPose7.p[11]";
connectAttr "rig:bindPose7.m[11]" "rig:bindPose7.p[12]";
connectAttr "rig:bindPose7.m[12]" "rig:bindPose7.p[13]";
connectAttr "rig:bindPose7.m[13]" "rig:bindPose7.p[14]";
connectAttr "rig:bindPose7.m[14]" "rig:bindPose7.p[15]";
connectAttr "rig:bindPose7.m[15]" "rig:bindPose7.p[16]";
connectAttr "rig:bindPose7.m[16]" "rig:bindPose7.p[17]";
connectAttr "rig:bindPose7.m[17]" "rig:bindPose7.p[18]";
connectAttr "rig:bindPose7.m[18]" "rig:bindPose7.p[19]";
connectAttr "rig:Group.msg" "rig:bindPose10.m[0]";
connectAttr "rig:Main.msg" "rig:bindPose10.m[1]";
connectAttr "rig:DeformationSystem.msg" "rig:bindPose10.m[2]";
connectAttr "rig:Root_M.msg" "rig:bindPose10.m[3]";
connectAttr "rig:RootPart1_M.msg" "rig:bindPose10.m[4]";
connectAttr "rig:RootPart2_M.msg" "rig:bindPose10.m[5]";
connectAttr "rig:Spine1_M.msg" "rig:bindPose10.m[6]";
connectAttr "rig:Spine2_M.msg" "rig:bindPose10.m[7]";
connectAttr "rig:Chest_M.msg" "rig:bindPose10.m[8]";
connectAttr "rig:Scapula_L.msg" "rig:bindPose10.m[9]";
connectAttr "rig:Shoulder_L.msg" "rig:bindPose10.m[10]";
connectAttr "rig:ShoulderPart1_L.msg" "rig:bindPose10.m[11]";
connectAttr "rig:ShoulderPart2_L.msg" "rig:bindPose10.m[12]";
connectAttr "rig:Elbow_L.msg" "rig:bindPose10.m[13]";
connectAttr "rig:ElbowPart1_L.msg" "rig:bindPose10.m[14]";
connectAttr "rig:ElbowPart2_L.msg" "rig:bindPose10.m[15]";
connectAttr "rig:Wrist_L.msg" "rig:bindPose10.m[16]";
connectAttr "rig:ThumbFinger1_L.msg" "rig:bindPose10.m[17]";
connectAttr "rig:ThumbFinger2_L.msg" "rig:bindPose10.m[18]";
connectAttr "rig:ThumbFinger3_L.msg" "rig:bindPose10.m[19]";
connectAttr "rig:IndexFinger1_L.msg" "rig:bindPose10.m[20]";
connectAttr "rig:IndexFinger2_L.msg" "rig:bindPose10.m[21]";
connectAttr "rig:IndexFinger3_L.msg" "rig:bindPose10.m[22]";
connectAttr "rig:MiddleFinger1_L.msg" "rig:bindPose10.m[23]";
connectAttr "rig:bindPose10.w" "rig:bindPose10.p[0]";
connectAttr "rig:bindPose10.m[0]" "rig:bindPose10.p[1]";
connectAttr "rig:bindPose10.m[1]" "rig:bindPose10.p[2]";
connectAttr "rig:bindPose10.m[2]" "rig:bindPose10.p[3]";
connectAttr "rig:bindPose10.m[3]" "rig:bindPose10.p[4]";
connectAttr "rig:bindPose10.m[4]" "rig:bindPose10.p[5]";
connectAttr "rig:bindPose10.m[5]" "rig:bindPose10.p[6]";
connectAttr "rig:bindPose10.m[6]" "rig:bindPose10.p[7]";
connectAttr "rig:bindPose10.m[7]" "rig:bindPose10.p[8]";
connectAttr "rig:bindPose10.m[8]" "rig:bindPose10.p[9]";
connectAttr "rig:bindPose10.m[9]" "rig:bindPose10.p[10]";
connectAttr "rig:bindPose10.m[10]" "rig:bindPose10.p[11]";
connectAttr "rig:bindPose10.m[11]" "rig:bindPose10.p[12]";
connectAttr "rig:bindPose10.m[12]" "rig:bindPose10.p[13]";
connectAttr "rig:bindPose10.m[13]" "rig:bindPose10.p[14]";
connectAttr "rig:bindPose10.m[14]" "rig:bindPose10.p[15]";
connectAttr "rig:bindPose10.m[15]" "rig:bindPose10.p[16]";
connectAttr "rig:bindPose10.m[16]" "rig:bindPose10.p[17]";
connectAttr "rig:bindPose10.m[17]" "rig:bindPose10.p[18]";
connectAttr "rig:bindPose10.m[18]" "rig:bindPose10.p[19]";
connectAttr "rig:bindPose10.m[16]" "rig:bindPose10.p[20]";
connectAttr "rig:IndexFinger1_L.msg" "rig:bindPose10.p[21]";
connectAttr "rig:IndexFinger2_L.msg" "rig:bindPose10.p[22]";
connectAttr "rig:bindPose10.m[16]" "rig:bindPose10.p[23]";
connectAttr "rig:IndexFinger1_L.bps" "rig:bindPose10.wm[20]";
connectAttr "rig:IndexFinger2_L.bps" "rig:bindPose10.wm[21]";
connectAttr "rig:IndexFinger3_L.bps" "rig:bindPose10.wm[22]";
connectAttr "rig:MiddleFinger1_L.bps" "rig:bindPose10.wm[23]";
connectAttr "rig:Group.msg" "rig:bindPose9.m[0]";
connectAttr "rig:Main.msg" "rig:bindPose9.m[1]";
connectAttr "rig:DeformationSystem.msg" "rig:bindPose9.m[2]";
connectAttr "rig:Root_M.msg" "rig:bindPose9.m[3]";
connectAttr "rig:RootPart1_M.msg" "rig:bindPose9.m[4]";
connectAttr "rig:RootPart2_M.msg" "rig:bindPose9.m[5]";
connectAttr "rig:Spine1_M.msg" "rig:bindPose9.m[6]";
connectAttr "rig:Spine2_M.msg" "rig:bindPose9.m[7]";
connectAttr "rig:Chest_M.msg" "rig:bindPose9.m[8]";
connectAttr "rig:Scapula_L.msg" "rig:bindPose9.m[9]";
connectAttr "rig:Shoulder_L.msg" "rig:bindPose9.m[10]";
connectAttr "rig:ShoulderPart1_L.msg" "rig:bindPose9.m[11]";
connectAttr "rig:ShoulderPart2_L.msg" "rig:bindPose9.m[12]";
connectAttr "rig:Elbow_L.msg" "rig:bindPose9.m[13]";
connectAttr "rig:ElbowPart1_L.msg" "rig:bindPose9.m[14]";
connectAttr "rig:ElbowPart2_L.msg" "rig:bindPose9.m[15]";
connectAttr "rig:Wrist_L.msg" "rig:bindPose9.m[16]";
connectAttr "rig:Cup_L.msg" "rig:bindPose9.m[17]";
connectAttr "rig:PinkyFinger1_L.msg" "rig:bindPose9.m[18]";
connectAttr "rig:PinkyFinger2_L.msg" "rig:bindPose9.m[19]";
connectAttr "rig:PinkyFinger3_L.msg" "rig:bindPose9.m[20]";
connectAttr "rig:RingFinger1_L.msg" "rig:bindPose9.m[21]";
connectAttr "rig:RingFinger2_L.msg" "rig:bindPose9.m[22]";
connectAttr "rig:RingFinger3_L.msg" "rig:bindPose9.m[23]";
connectAttr "rig:bindPose9.w" "rig:bindPose9.p[0]";
connectAttr "rig:bindPose9.m[0]" "rig:bindPose9.p[1]";
connectAttr "rig:bindPose9.m[1]" "rig:bindPose9.p[2]";
connectAttr "rig:bindPose9.m[2]" "rig:bindPose9.p[3]";
connectAttr "rig:bindPose9.m[3]" "rig:bindPose9.p[4]";
connectAttr "rig:bindPose9.m[4]" "rig:bindPose9.p[5]";
connectAttr "rig:bindPose9.m[5]" "rig:bindPose9.p[6]";
connectAttr "rig:bindPose9.m[6]" "rig:bindPose9.p[7]";
connectAttr "rig:bindPose9.m[7]" "rig:bindPose9.p[8]";
connectAttr "rig:bindPose9.m[8]" "rig:bindPose9.p[9]";
connectAttr "rig:bindPose9.m[9]" "rig:bindPose9.p[10]";
connectAttr "rig:bindPose9.m[10]" "rig:bindPose9.p[11]";
connectAttr "rig:bindPose9.m[11]" "rig:bindPose9.p[12]";
connectAttr "rig:bindPose9.m[12]" "rig:bindPose9.p[13]";
connectAttr "rig:bindPose9.m[13]" "rig:bindPose9.p[14]";
connectAttr "rig:bindPose9.m[14]" "rig:bindPose9.p[15]";
connectAttr "rig:bindPose9.m[15]" "rig:bindPose9.p[16]";
connectAttr "rig:bindPose9.m[16]" "rig:bindPose9.p[17]";
connectAttr "rig:bindPose9.m[17]" "rig:bindPose9.p[18]";
connectAttr "rig:bindPose9.m[18]" "rig:bindPose9.p[19]";
connectAttr "rig:bindPose9.m[19]" "rig:bindPose9.p[20]";
connectAttr "rig:bindPose9.m[17]" "rig:bindPose9.p[21]";
connectAttr "rig:RingFinger1_L.msg" "rig:bindPose9.p[22]";
connectAttr "rig:RingFinger2_L.msg" "rig:bindPose9.p[23]";
connectAttr "rig:RingFinger1_L.bps" "rig:bindPose9.wm[21]";
connectAttr "rig:RingFinger2_L.bps" "rig:bindPose9.wm[22]";
connectAttr "rig:RingFinger3_L.bps" "rig:bindPose9.wm[23]";
connectAttr "rig:RootX_M.legLock" "rig:LegLockUnitConversion.i";
connectAttr "rig:LegLockUnitConversion.o" "rig:LegLockReverse.ix";
connectAttr "rig:unitConversion1.o" "rig:InbetweenUnTwistDividerNeck1_M.i1x";
connectAttr "rig:TwistBalancerNeck1_M.rx" "rig:unitConversion1.i";
connectAttr "rig:InbetweenUnTwistDividerNeck1_M.ox" "rig:unitConversion2.i";
connectAttr "rig:unitConversion3.o" "rig:InbetweenUnTwistDividerNeck2_M.i1x";
connectAttr "rig:TwistBalancerNeck1_M.rx" "rig:unitConversion3.i";
connectAttr "rig:InbetweenUnTwistDividerNeck2_M.ox" "rig:unitConversion4.i";
connectAttr "rig:IKCurveInfoNormalizeSpine_M.ox" "rig:IKCurveInfoAllMultiplySpine_M.i1x"
		;
connectAttr "rig:Main.sx" "rig:IKCurveInfoAllMultiplySpine_M.i2x";
connectAttr "rig:FKIKBlendLegsetRange_R.ox" "rig:FKIKBlendLegCondition_R.cfg";
connectAttr "rig:FKIKSpine_M.FKIKBlend" "rig:FKIKBlendSpineUnitConversion_M.i";
connectAttr "rig:FKIKBlendSpineUnitConversion_M.o" "rig:FKIKBlendSpineReverse_M.ix"
		;
connectAttr "rig:FKIKSpine_M.autoVis" "rig:FKIKBlendSpineCondition_M.ft";
connectAttr "rig:FKIKSpine_M.IKVis" "rig:FKIKBlendSpineCondition_M.ctr";
connectAttr "rig:FKIKSpine_M.FKVis" "rig:FKIKBlendSpineCondition_M.ctg";
connectAttr "rig:FKIKSpine_M.FKIKBlend" "rig:FKIKBlendSpineCondition_M.cfr";
connectAttr "rig:FKIKBlendSpinesetRange_M.ox" "rig:FKIKBlendSpineCondition_M.cfg"
		;
connectAttr "rig:FKIKSpine_M.FKIKBlend" "rig:FKIKBlendSpinesetRange_M.vx";
connectAttr "rig:FKIKBlendLegsetRange_L.ox" "rig:FKIKBlendLegCondition_L.cfg";
connectAttr "rig:FKIKArm_L.FKIKBlend" "rig:FKIKBlendArmUnitConversion_L.i";
connectAttr "rig:FKIKBlendArmUnitConversion_L.o" "rig:FKIKBlendArmReverse_L.ix";
connectAttr "rig:FKIKArm_L.autoVis" "rig:FKIKBlendArmCondition_L.ft";
connectAttr "rig:FKIKArm_L.IKVis" "rig:FKIKBlendArmCondition_L.ctr";
connectAttr "rig:FKIKArm_L.FKVis" "rig:FKIKBlendArmCondition_L.ctg";
connectAttr "rig:FKIKArm_L.FKIKBlend" "rig:FKIKBlendArmCondition_L.cfr";
connectAttr "rig:FKIKBlendArmsetRange_L.ox" "rig:FKIKBlendArmCondition_L.cfg";
connectAttr "rig:FKIKArm_L.FKIKBlend" "rig:FKIKBlendArmsetRange_L.vx";
connectAttr "rig:FKAnkle_R.s" "rig:ScaleBlendAnkle_R.c2";
connectAttr "rig:FKKnee_R.s" "rig:ScaleBlendKnee_R.c2";
connectAttr "rig:volumeBlendLegBlendTwo_R.o" "rig:ScaleBlendKnee_R.c1g";
connectAttr "rig:volumeBlendLegBlendTwo_R.o" "rig:ScaleBlendKnee_R.c1b";
connectAttr "rig:FKHip_R.s" "rig:ScaleBlendHip_R.c2";
connectAttr "rig:volumeBlendLegBlendTwo_R.o" "rig:ScaleBlendHip_R.c1g";
connectAttr "rig:volumeBlendLegBlendTwo_R.o" "rig:ScaleBlendHip_R.c1b";
connectAttr "rig:volumeBlendArmBlendTwo_R.o" "rig:ScaleBlendElbow_R.c1g";
connectAttr "rig:volumeBlendArmBlendTwo_R.o" "rig:ScaleBlendElbow_R.c1b";
connectAttr "rig:volumeBlendArmBlendTwo_R.o" "rig:ScaleBlendShoulder_R.c1g";
connectAttr "rig:volumeBlendArmBlendTwo_R.o" "rig:ScaleBlendShoulder_R.c1b";
connectAttr "rig:FKChest_M.s" "rig:ScaleBlendChest_M.c2";
connectAttr "rig:FKIKBlendSpineUnitConversion_M.o" "rig:ScaleBlendChest_M.b";
connectAttr "rig:IKScaleChestMultiplyDivide_M.o" "rig:ScaleBlendChest_M.c1";
connectAttr "rig:FKSpine2_M.s" "rig:ScaleBlendSpine2_M.c2";
connectAttr "rig:FKIKBlendSpineUnitConversion_M.o" "rig:ScaleBlendSpine2_M.b";
connectAttr "rig:IKScaleSpine2MultiplyDivide_M.o" "rig:ScaleBlendSpine2_M.c1";
connectAttr "rig:FKSpine1_M.s" "rig:ScaleBlendSpine1_M.c2";
connectAttr "rig:FKIKBlendSpineUnitConversion_M.o" "rig:ScaleBlendSpine1_M.b";
connectAttr "rig:IKScaleSpine1MultiplyDivide_M.o" "rig:ScaleBlendSpine1_M.c1";
connectAttr "rig:FKRootPart2_M.s" "rig:ScaleBlendRootPart2_M.c2";
connectAttr "rig:FKIKBlendSpineUnitConversion_M.o" "rig:ScaleBlendRootPart2_M.b"
		;
connectAttr "rig:IKScaleRootPart2MultiplyDivide_M.o" "rig:ScaleBlendRootPart2_M.c1"
		;
connectAttr "rig:FKRootPart1_M.s" "rig:ScaleBlendRootPart1_M.c2";
connectAttr "rig:FKIKBlendSpineUnitConversion_M.o" "rig:ScaleBlendRootPart1_M.b"
		;
connectAttr "rig:IKScaleRootPart1MultiplyDivide_M.o" "rig:ScaleBlendRootPart1_M.c1"
		;
connectAttr "rig:FKRoot_M.s" "rig:ScaleBlendRoot_M.c2";
connectAttr "rig:FKIKBlendSpineUnitConversion_M.o" "rig:ScaleBlendRoot_M.b";
connectAttr "rig:IKScaleRootMultiplyDivide_M.o" "rig:ScaleBlendRoot_M.c1";
connectAttr "rig:FKAnkle_L.s" "rig:ScaleBlendAnkle_L.c2";
connectAttr "rig:FKKnee_L.s" "rig:ScaleBlendKnee_L.c2";
connectAttr "rig:volumeBlendLegBlendTwo_L.o" "rig:ScaleBlendKnee_L.c1g";
connectAttr "rig:volumeBlendLegBlendTwo_L.o" "rig:ScaleBlendKnee_L.c1b";
connectAttr "rig:FKHip_L.s" "rig:ScaleBlendHip_L.c2";
connectAttr "rig:volumeBlendLegBlendTwo_L.o" "rig:ScaleBlendHip_L.c1g";
connectAttr "rig:volumeBlendLegBlendTwo_L.o" "rig:ScaleBlendHip_L.c1b";
connectAttr "rig:FKWrist_L.s" "rig:ScaleBlendWrist_L.c2";
connectAttr "rig:FKIKBlendArmUnitConversion_L.o" "rig:ScaleBlendWrist_L.b";
connectAttr "rig:FKElbow_L.s" "rig:ScaleBlendElbow_L.c2";
connectAttr "rig:FKIKBlendArmUnitConversion_L.o" "rig:ScaleBlendElbow_L.b";
connectAttr "rig:volumeBlendArmBlendTwo_L.o" "rig:ScaleBlendElbow_L.c1g";
connectAttr "rig:volumeBlendArmBlendTwo_L.o" "rig:ScaleBlendElbow_L.c1b";
connectAttr "rig:FKShoulder_L.s" "rig:ScaleBlendShoulder_L.c2";
connectAttr "rig:FKIKBlendArmUnitConversion_L.o" "rig:ScaleBlendShoulder_L.b";
connectAttr "rig:volumeBlendArmBlendTwo_L.o" "rig:ScaleBlendShoulder_L.c1g";
connectAttr "rig:volumeBlendArmBlendTwo_L.o" "rig:ScaleBlendShoulder_L.c1b";
connectAttr "rig:IKSquashDistributNormalizerBRootPart1_M.o1" "rig:IKScaleRootPart1MultiplyDivide_M.i2y"
		;
connectAttr "rig:IKSquashDistributNormalizerBRootPart1_M.o1" "rig:IKScaleRootPart1MultiplyDivide_M.i2z"
		;
connectAttr "rig:IKSquashDistributNormalizerBRootPart2_M.o1" "rig:IKScaleRootPart2MultiplyDivide_M.i2y"
		;
connectAttr "rig:IKSquashDistributNormalizerBRootPart2_M.o1" "rig:IKScaleRootPart2MultiplyDivide_M.i2z"
		;
connectAttr "rig:IKSquashDistributNormalizerBSpine1_M.o1" "rig:IKScaleSpine1MultiplyDivide_M.i2y"
		;
connectAttr "rig:IKSquashDistributNormalizerBSpine1_M.o1" "rig:IKScaleSpine1MultiplyDivide_M.i2z"
		;
connectAttr "rig:IKSquashDistributNormalizerBSpine2_M.o1" "rig:IKScaleSpine2MultiplyDivide_M.i2y"
		;
connectAttr "rig:IKSquashDistributNormalizerBSpine2_M.o1" "rig:IKScaleSpine2MultiplyDivide_M.i2z"
		;
connectAttr "rig:IKmessureBlendStretchLeg_R.o" "rig:IKmessureDivLeg_R.i1x";
connectAttr "rig:IKSetRangeAntiPopLeg_R.ox" "rig:IKmessureBlendAntiPopLeg_R.ab";
connectAttr "rig:IKmessureBlendAntiPopLeg_R.o" "rig:IKdistanceClampLeg_R.ipr";
connectAttr "rig:IKSetRangeStretchLeg_R.ox" "rig:IKmessureBlendStretchLeg_R.ab";
connectAttr "rig:IKdistanceClampLeg_R.opr" "rig:IKmessureBlendStretchLeg_R.i[0]"
		;
connectAttr "rig:IKmessureBlendAntiPopLeg_R.o" "rig:IKmessureBlendStretchLeg_R.i[1]"
		;
connectAttr "rig:IKmessureBlendStretchArm_R.o" "rig:IKmessureDivArm_R.i1x";
connectAttr "rig:IKSetRangeAntiPopArm_R.ox" "rig:IKmessureBlendAntiPopArm_R.ab";
connectAttr "rig:IKmessureBlendAntiPopArm_R.o" "rig:IKdistanceClampArm_R.ipr";
connectAttr "rig:IKSetRangeStretchArm_R.ox" "rig:IKmessureBlendStretchArm_R.ab";
connectAttr "rig:IKdistanceClampArm_R.opr" "rig:IKmessureBlendStretchArm_R.i[0]"
		;
connectAttr "rig:IKmessureBlendAntiPopArm_R.o" "rig:IKmessureBlendStretchArm_R.i[1]"
		;
connectAttr "rig:IKmessureBlendStretchLeg_L.o" "rig:IKmessureDivLeg_L.i1x";
connectAttr "rig:IKSetRangeAntiPopLeg_L.ox" "rig:IKmessureBlendAntiPopLeg_L.ab";
connectAttr "rig:IKmessureBlendAntiPopLeg_L.o" "rig:IKdistanceClampLeg_L.ipr";
connectAttr "rig:IKSetRangeStretchLeg_L.ox" "rig:IKmessureBlendStretchLeg_L.ab";
connectAttr "rig:IKdistanceClampLeg_L.opr" "rig:IKmessureBlendStretchLeg_L.i[0]"
		;
connectAttr "rig:IKmessureBlendAntiPopLeg_L.o" "rig:IKmessureBlendStretchLeg_L.i[1]"
		;
connectAttr "rig:IKmessureBlendStretchArm_L.o" "rig:IKmessureDivArm_L.i1x";
connectAttr "rig:IKSetRangeAntiPopArm_L.ox" "rig:IKmessureBlendAntiPopArm_L.ab";
connectAttr "rig:IKmessureBlendAntiPopArm_L.o" "rig:IKdistanceClampArm_L.ipr";
connectAttr "rig:IKSetRangeStretchArm_L.ox" "rig:IKmessureBlendStretchArm_L.ab";
connectAttr "rig:IKdistanceClampArm_L.opr" "rig:IKmessureBlendStretchArm_L.i[0]"
		;
connectAttr "rig:IKmessureBlendAntiPopArm_L.o" "rig:IKmessureBlendStretchArm_L.i[1]"
		;
connectAttr "rig:HipSwinger_M.stabilize" "rig:HipSwingerStabilizerUnitConversion.i"
		;
connectAttr "rig:HipSwingerStabilizerUnitConversion.o" "rig:HipSwingerStabilizerReverse.ix"
		;
connectAttr "rig:RootX_M.CenterBtwFeet" "rig:CenterBtwLegsUnitConversion.i";
connectAttr "rig:CenterBtwLegsUnitConversion.o" "rig:CenterBtwLegsUnitReverse.ix"
		;
connectAttr "rig:unitConversion30.o" "rig:twistAmountDivideKneePart0_R.i1x";
connectAttr "rig:Hip_R.twistAmount" "rig:twistAmountDivideKneePart0_R.i2x";
connectAttr "rig:twistAmountDivideKneePart0_R.ox" "rig:twistAdditionKneePart0_R.i1[0]"
		;
connectAttr "rig:TwistBalancerKnee_R.rx" "rig:unitConversion30.i";
connectAttr "rig:twistAdditionKneePart0_R.o1" "rig:unitConversion31.i";
connectAttr "rig:unitConversion32.o" "rig:twistAmountDivideKneePart1_R.i1x";
connectAttr "rig:HipPart1_R.twistAmount" "rig:twistAmountDivideKneePart1_R.i2x";
connectAttr "rig:twistAmountDivideKneePart1_R.ox" "rig:twistAdditionKneePart1_R.i1[0]"
		;
connectAttr "rig:TwistBalancerKnee_R.rx" "rig:unitConversion32.i";
connectAttr "rig:twistAdditionKneePart1_R.o1" "rig:unitConversion33.i";
connectAttr "rig:unitConversion34.o" "rig:twistAmountDivideKneePart2_R.i1x";
connectAttr "rig:HipPart2_R.twistAmount" "rig:twistAmountDivideKneePart2_R.i2x";
connectAttr "rig:twistAmountDivideKneePart2_R.ox" "rig:twistAdditionKneePart2_R.i1[0]"
		;
connectAttr "rig:TwistBalancerKnee_R.rx" "rig:unitConversion34.i";
connectAttr "rig:twistAdditionKneePart2_R.o1" "rig:unitConversion35.i";
connectAttr "rig:Hip_R.twistAmount" "rig:twistAmountDivideHipPart0_R.i2x";
connectAttr "rig:unitConversion36.o" "rig:twistAmountDivideHipPart0_R.i1x";
connectAttr "rig:twistAmountDivideHipPart0_R.ox" "rig:twistAdditionHipPart0_R.i1[0]"
		;
connectAttr "rig:Hip_R.twistAddition" "rig:twistAdditionHipPart0_R.i1[1]";
connectAttr "rig:twistAmountDivideKneePart0_R.ox" "rig:twistAdditionHipPart0_R.i1[2]"
		;
connectAttr "rig:TwistBalancerHip_R.rx" "rig:unitConversion36.i";
connectAttr "rig:twistAdditionHipPart0_R.o1" "rig:unitConversion37.i";
connectAttr "rig:HipPart1_R.twistAmount" "rig:twistAmountDivideHipPart1_R.i2x";
connectAttr "rig:unitConversion38.o" "rig:twistAmountDivideHipPart1_R.i1x";
connectAttr "rig:twistAmountDivideHipPart1_R.ox" "rig:twistAdditionHipPart1_R.i1[0]"
		;
connectAttr "rig:HipPart1_R.twistAddition" "rig:twistAdditionHipPart1_R.i1[1]";
connectAttr "rig:twistAmountDivideKneePart1_R.ox" "rig:twistAdditionHipPart1_R.i1[2]"
		;
connectAttr "rig:TwistBalancerHip_R.rx" "rig:unitConversion38.i";
connectAttr "rig:twistAdditionHipPart1_R.o1" "rig:unitConversion39.i";
connectAttr "rig:HipPart2_R.twistAmount" "rig:twistAmountDivideHipPart2_R.i2x";
connectAttr "rig:unitConversion40.o" "rig:twistAmountDivideHipPart2_R.i1x";
connectAttr "rig:twistAmountDivideHipPart2_R.ox" "rig:twistAdditionHipPart2_R.i1[0]"
		;
connectAttr "rig:HipPart2_R.twistAddition" "rig:twistAdditionHipPart2_R.i1[1]";
connectAttr "rig:twistAmountDivideKneePart2_R.ox" "rig:twistAdditionHipPart2_R.i1[2]"
		;
connectAttr "rig:TwistBalancerHip_R.rx" "rig:unitConversion40.i";
connectAttr "rig:twistAdditionHipPart2_R.o1" "rig:unitConversion41.i";
connectAttr "rig:unitConversion42.o" "rig:twistAmountDivideWristPart0_R.i1x";
connectAttr "rig:Elbow_R.twistAmount" "rig:twistAmountDivideWristPart0_R.i2x";
connectAttr "rig:twistAmountDivideWristPart0_R.ox" "rig:twistAdditionWristPart0_R.i1[0]"
		;
connectAttr "rig:TwistBalancerWrist_R.rx" "rig:unitConversion42.i";
connectAttr "rig:twistAdditionWristPart0_R.o1" "rig:unitConversion43.i";
connectAttr "rig:unitConversion44.o" "rig:twistAmountDivideWristPart1_R.i1x";
connectAttr "rig:ElbowPart1_R.twistAmount" "rig:twistAmountDivideWristPart1_R.i2x"
		;
connectAttr "rig:twistAmountDivideWristPart1_R.ox" "rig:twistAdditionWristPart1_R.i1[0]"
		;
connectAttr "rig:TwistBalancerWrist_R.rx" "rig:unitConversion44.i";
connectAttr "rig:twistAdditionWristPart1_R.o1" "rig:unitConversion45.i";
connectAttr "rig:unitConversion46.o" "rig:twistAmountDivideWristPart2_R.i1x";
connectAttr "rig:ElbowPart2_R.twistAmount" "rig:twistAmountDivideWristPart2_R.i2x"
		;
connectAttr "rig:twistAmountDivideWristPart2_R.ox" "rig:twistAdditionWristPart2_R.i1[0]"
		;
connectAttr "rig:TwistBalancerWrist_R.rx" "rig:unitConversion46.i";
connectAttr "rig:twistAdditionWristPart2_R.o1" "rig:unitConversion47.i";
connectAttr "rig:Elbow_R.twistAmount" "rig:twistAmountDivideElbowPart0_R.i2x";
connectAttr "rig:unitConversion48.o" "rig:twistAmountDivideElbowPart0_R.i1x";
connectAttr "rig:twistAmountDivideElbowPart0_R.ox" "rig:twistAdditionElbowPart0_R.i1[0]"
		;
connectAttr "rig:Elbow_R.twistAddition" "rig:twistAdditionElbowPart0_R.i1[1]";
connectAttr "rig:twistAmountDivideWristPart0_R.ox" "rig:twistAdditionElbowPart0_R.i1[2]"
		;
connectAttr "rig:TwistBalancerElbow_R.rx" "rig:unitConversion48.i";
connectAttr "rig:twistAdditionElbowPart0_R.o1" "rig:unitConversion49.i";
connectAttr "rig:ElbowPart1_R.twistAmount" "rig:twistAmountDivideElbowPart1_R.i2x"
		;
connectAttr "rig:unitConversion50.o" "rig:twistAmountDivideElbowPart1_R.i1x";
connectAttr "rig:twistAmountDivideElbowPart1_R.ox" "rig:twistAdditionElbowPart1_R.i1[0]"
		;
connectAttr "rig:ElbowPart1_R.twistAddition" "rig:twistAdditionElbowPart1_R.i1[1]"
		;
connectAttr "rig:twistAmountDivideWristPart1_R.ox" "rig:twistAdditionElbowPart1_R.i1[2]"
		;
connectAttr "rig:TwistBalancerElbow_R.rx" "rig:unitConversion50.i";
connectAttr "rig:twistAdditionElbowPart1_R.o1" "rig:unitConversion51.i";
connectAttr "rig:ElbowPart2_R.twistAmount" "rig:twistAmountDivideElbowPart2_R.i2x"
		;
connectAttr "rig:unitConversion52.o" "rig:twistAmountDivideElbowPart2_R.i1x";
connectAttr "rig:twistAmountDivideElbowPart2_R.ox" "rig:twistAdditionElbowPart2_R.i1[0]"
		;
connectAttr "rig:ElbowPart2_R.twistAddition" "rig:twistAdditionElbowPart2_R.i1[1]"
		;
connectAttr "rig:twistAmountDivideWristPart2_R.ox" "rig:twistAdditionElbowPart2_R.i1[2]"
		;
connectAttr "rig:TwistBalancerElbow_R.rx" "rig:unitConversion52.i";
connectAttr "rig:twistAdditionElbowPart2_R.o1" "rig:unitConversion53.i";
connectAttr "rig:Shoulder_R.twistAmount" "rig:twistAmountDivideShoulderPart0_R.i2x"
		;
connectAttr "rig:unitConversion54.o" "rig:twistAmountDivideShoulderPart0_R.i1x";
connectAttr "rig:twistAmountDivideShoulderPart0_R.ox" "rig:twistAdditionShoulderPart0_R.i1[0]"
		;
connectAttr "rig:Shoulder_R.twistAddition" "rig:twistAdditionShoulderPart0_R.i1[1]"
		;
connectAttr "rig:TwistBalancerShoulder_R.rx" "rig:unitConversion54.i";
connectAttr "rig:twistAdditionShoulderPart0_R.o1" "rig:unitConversion55.i";
connectAttr "rig:ShoulderPart1_R.twistAmount" "rig:twistAmountDivideShoulderPart1_R.i2x"
		;
connectAttr "rig:unitConversion56.o" "rig:twistAmountDivideShoulderPart1_R.i1x";
connectAttr "rig:twistAmountDivideShoulderPart1_R.ox" "rig:twistAdditionShoulderPart1_R.i1[0]"
		;
connectAttr "rig:ShoulderPart1_R.twistAddition" "rig:twistAdditionShoulderPart1_R.i1[1]"
		;
connectAttr "rig:TwistBalancerShoulder_R.rx" "rig:unitConversion56.i";
connectAttr "rig:twistAdditionShoulderPart1_R.o1" "rig:unitConversion57.i";
connectAttr "rig:ShoulderPart2_R.twistAmount" "rig:twistAmountDivideShoulderPart2_R.i2x"
		;
connectAttr "rig:unitConversion58.o" "rig:twistAmountDivideShoulderPart2_R.i1x";
connectAttr "rig:twistAmountDivideShoulderPart2_R.ox" "rig:twistAdditionShoulderPart2_R.i1[0]"
		;
connectAttr "rig:ShoulderPart2_R.twistAddition" "rig:twistAdditionShoulderPart2_R.i1[1]"
		;
connectAttr "rig:TwistBalancerShoulder_R.rx" "rig:unitConversion58.i";
connectAttr "rig:twistAdditionShoulderPart2_R.o1" "rig:unitConversion59.i";
connectAttr "rig:unitConversion60.o" "rig:twistAmountDivideKneePart0_L.i1x";
connectAttr "rig:Hip_L.twistAmount" "rig:twistAmountDivideKneePart0_L.i2x";
connectAttr "rig:twistAmountDivideKneePart0_L.ox" "rig:twistAdditionKneePart0_L.i1[0]"
		;
connectAttr "rig:TwistBalancerKnee_L.rx" "rig:unitConversion60.i";
connectAttr "rig:twistAdditionKneePart0_L.o1" "rig:unitConversion61.i";
connectAttr "rig:unitConversion62.o" "rig:twistAmountDivideKneePart1_L.i1x";
connectAttr "rig:HipPart1_L.twistAmount" "rig:twistAmountDivideKneePart1_L.i2x";
connectAttr "rig:twistAmountDivideKneePart1_L.ox" "rig:twistAdditionKneePart1_L.i1[0]"
		;
connectAttr "rig:TwistBalancerKnee_L.rx" "rig:unitConversion62.i";
connectAttr "rig:twistAdditionKneePart1_L.o1" "rig:unitConversion63.i";
connectAttr "rig:unitConversion64.o" "rig:twistAmountDivideKneePart2_L.i1x";
connectAttr "rig:HipPart2_L.twistAmount" "rig:twistAmountDivideKneePart2_L.i2x";
connectAttr "rig:twistAmountDivideKneePart2_L.ox" "rig:twistAdditionKneePart2_L.i1[0]"
		;
connectAttr "rig:TwistBalancerKnee_L.rx" "rig:unitConversion64.i";
connectAttr "rig:twistAdditionKneePart2_L.o1" "rig:unitConversion65.i";
connectAttr "rig:Hip_L.twistAmount" "rig:twistAmountDivideHipPart0_L.i2x";
connectAttr "rig:unitConversion66.o" "rig:twistAmountDivideHipPart0_L.i1x";
connectAttr "rig:twistAmountDivideHipPart0_L.ox" "rig:twistAdditionHipPart0_L.i1[0]"
		;
connectAttr "rig:Hip_L.twistAddition" "rig:twistAdditionHipPart0_L.i1[1]";
connectAttr "rig:twistAmountDivideKneePart0_L.ox" "rig:twistAdditionHipPart0_L.i1[2]"
		;
connectAttr "rig:TwistBalancerHip_L.rx" "rig:unitConversion66.i";
connectAttr "rig:twistAdditionHipPart0_L.o1" "rig:unitConversion67.i";
connectAttr "rig:HipPart1_L.twistAmount" "rig:twistAmountDivideHipPart1_L.i2x";
connectAttr "rig:unitConversion68.o" "rig:twistAmountDivideHipPart1_L.i1x";
connectAttr "rig:twistAmountDivideHipPart1_L.ox" "rig:twistAdditionHipPart1_L.i1[0]"
		;
connectAttr "rig:HipPart1_L.twistAddition" "rig:twistAdditionHipPart1_L.i1[1]";
connectAttr "rig:twistAmountDivideKneePart1_L.ox" "rig:twistAdditionHipPart1_L.i1[2]"
		;
connectAttr "rig:TwistBalancerHip_L.rx" "rig:unitConversion68.i";
connectAttr "rig:twistAdditionHipPart1_L.o1" "rig:unitConversion69.i";
connectAttr "rig:HipPart2_L.twistAmount" "rig:twistAmountDivideHipPart2_L.i2x";
connectAttr "rig:unitConversion70.o" "rig:twistAmountDivideHipPart2_L.i1x";
connectAttr "rig:twistAmountDivideHipPart2_L.ox" "rig:twistAdditionHipPart2_L.i1[0]"
		;
connectAttr "rig:HipPart2_L.twistAddition" "rig:twistAdditionHipPart2_L.i1[1]";
connectAttr "rig:twistAmountDivideKneePart2_L.ox" "rig:twistAdditionHipPart2_L.i1[2]"
		;
connectAttr "rig:TwistBalancerHip_L.rx" "rig:unitConversion70.i";
connectAttr "rig:twistAdditionHipPart2_L.o1" "rig:unitConversion71.i";
connectAttr "rig:unitConversion72.o" "rig:twistAmountDivideWristPart0_L.i1x";
connectAttr "rig:Elbow_L.twistAmount" "rig:twistAmountDivideWristPart0_L.i2x";
connectAttr "rig:twistAmountDivideWristPart0_L.ox" "rig:twistAdditionWristPart0_L.i1[0]"
		;
connectAttr "rig:TwistBalancerWrist_L.rx" "rig:unitConversion72.i";
connectAttr "rig:twistAdditionWristPart0_L.o1" "rig:unitConversion73.i";
connectAttr "rig:unitConversion74.o" "rig:twistAmountDivideWristPart1_L.i1x";
connectAttr "rig:ElbowPart1_L.twistAmount" "rig:twistAmountDivideWristPart1_L.i2x"
		;
connectAttr "rig:twistAmountDivideWristPart1_L.ox" "rig:twistAdditionWristPart1_L.i1[0]"
		;
connectAttr "rig:TwistBalancerWrist_L.rx" "rig:unitConversion74.i";
connectAttr "rig:twistAdditionWristPart1_L.o1" "rig:unitConversion75.i";
connectAttr "rig:unitConversion76.o" "rig:twistAmountDivideWristPart2_L.i1x";
connectAttr "rig:ElbowPart2_L.twistAmount" "rig:twistAmountDivideWristPart2_L.i2x"
		;
connectAttr "rig:twistAmountDivideWristPart2_L.ox" "rig:twistAdditionWristPart2_L.i1[0]"
		;
connectAttr "rig:TwistBalancerWrist_L.rx" "rig:unitConversion76.i";
connectAttr "rig:twistAdditionWristPart2_L.o1" "rig:unitConversion77.i";
connectAttr "rig:Elbow_L.twistAmount" "rig:twistAmountDivideElbowPart0_L.i2x";
connectAttr "rig:unitConversion78.o" "rig:twistAmountDivideElbowPart0_L.i1x";
connectAttr "rig:twistAmountDivideElbowPart0_L.ox" "rig:twistAdditionElbowPart0_L.i1[0]"
		;
connectAttr "rig:Elbow_L.twistAddition" "rig:twistAdditionElbowPart0_L.i1[1]";
connectAttr "rig:twistAmountDivideWristPart0_L.ox" "rig:twistAdditionElbowPart0_L.i1[2]"
		;
connectAttr "rig:TwistBalancerElbow_L.rx" "rig:unitConversion78.i";
connectAttr "rig:twistAdditionElbowPart0_L.o1" "rig:unitConversion79.i";
connectAttr "rig:ElbowPart1_L.twistAmount" "rig:twistAmountDivideElbowPart1_L.i2x"
		;
connectAttr "rig:unitConversion80.o" "rig:twistAmountDivideElbowPart1_L.i1x";
connectAttr "rig:twistAmountDivideElbowPart1_L.ox" "rig:twistAdditionElbowPart1_L.i1[0]"
		;
connectAttr "rig:ElbowPart1_L.twistAddition" "rig:twistAdditionElbowPart1_L.i1[1]"
		;
connectAttr "rig:twistAmountDivideWristPart1_L.ox" "rig:twistAdditionElbowPart1_L.i1[2]"
		;
connectAttr "rig:TwistBalancerElbow_L.rx" "rig:unitConversion80.i";
connectAttr "rig:twistAdditionElbowPart1_L.o1" "rig:unitConversion81.i";
connectAttr "rig:ElbowPart2_L.twistAmount" "rig:twistAmountDivideElbowPart2_L.i2x"
		;
connectAttr "rig:unitConversion82.o" "rig:twistAmountDivideElbowPart2_L.i1x";
connectAttr "rig:twistAmountDivideElbowPart2_L.ox" "rig:twistAdditionElbowPart2_L.i1[0]"
		;
connectAttr "rig:ElbowPart2_L.twistAddition" "rig:twistAdditionElbowPart2_L.i1[1]"
		;
connectAttr "rig:twistAmountDivideWristPart2_L.ox" "rig:twistAdditionElbowPart2_L.i1[2]"
		;
connectAttr "rig:TwistBalancerElbow_L.rx" "rig:unitConversion82.i";
connectAttr "rig:twistAdditionElbowPart2_L.o1" "rig:unitConversion83.i";
connectAttr "rig:Shoulder_L.twistAmount" "rig:twistAmountDivideShoulderPart0_L.i2x"
		;
connectAttr "rig:unitConversion84.o" "rig:twistAmountDivideShoulderPart0_L.i1x";
connectAttr "rig:twistAmountDivideShoulderPart0_L.ox" "rig:twistAdditionShoulderPart0_L.i1[0]"
		;
connectAttr "rig:Shoulder_L.twistAddition" "rig:twistAdditionShoulderPart0_L.i1[1]"
		;
connectAttr "rig:TwistBalancerShoulder_L.rx" "rig:unitConversion84.i";
connectAttr "rig:twistAdditionShoulderPart0_L.o1" "rig:unitConversion85.i";
connectAttr "rig:ShoulderPart1_L.twistAmount" "rig:twistAmountDivideShoulderPart1_L.i2x"
		;
connectAttr "rig:unitConversion86.o" "rig:twistAmountDivideShoulderPart1_L.i1x";
connectAttr "rig:twistAmountDivideShoulderPart1_L.ox" "rig:twistAdditionShoulderPart1_L.i1[0]"
		;
connectAttr "rig:ShoulderPart1_L.twistAddition" "rig:twistAdditionShoulderPart1_L.i1[1]"
		;
connectAttr "rig:TwistBalancerShoulder_L.rx" "rig:unitConversion86.i";
connectAttr "rig:twistAdditionShoulderPart1_L.o1" "rig:unitConversion87.i";
connectAttr "rig:ShoulderPart2_L.twistAmount" "rig:twistAmountDivideShoulderPart2_L.i2x"
		;
connectAttr "rig:unitConversion88.o" "rig:twistAmountDivideShoulderPart2_L.i1x";
connectAttr "rig:twistAmountDivideShoulderPart2_L.ox" "rig:twistAdditionShoulderPart2_L.i1[0]"
		;
connectAttr "rig:ShoulderPart2_L.twistAddition" "rig:twistAdditionShoulderPart2_L.i1[1]"
		;
connectAttr "rig:TwistBalancerShoulder_L.rx" "rig:unitConversion88.i";
connectAttr "rig:twistAdditionShoulderPart2_L.o1" "rig:unitConversion89.i";
connectAttr "rig:IKmessureDivLeg_R.ox" "rig:volume1OverLeg_R.i2x";
connectAttr "rig:volume1OverLeg_R.ox" "rig:volumepowLeg_R.i1x";
connectAttr "rig:multWithStretchyLeg_R.ox" "rig:volumeBlendLegBlendTwo_R.ab";
connectAttr "rig:volumepowLeg_R.ox" "rig:volumeBlendLegBlendTwo_R.i[1]";
connectAttr "rig:IKmessureDivArm_R.ox" "rig:volume1OverArm_R.i2x";
connectAttr "rig:volume1OverArm_R.ox" "rig:volumepowArm_R.i1x";
connectAttr "rig:multWithStretchyArm_R.ox" "rig:volumeBlendArmBlendTwo_R.ab";
connectAttr "rig:volumepowArm_R.ox" "rig:volumeBlendArmBlendTwo_R.i[1]";
connectAttr "rig:IKCurveInfoAllMultiplySpine_M.ox" "rig:volume1OverSpine_M.i2x";
connectAttr "rig:volume1OverSpine_M.ox" "rig:volumepowSpine_M.i1x";
connectAttr "rig:multWithStretchySpine_M.ox" "rig:volumeBlendSpineBlendTwo_M.ab"
		;
connectAttr "rig:volumepowSpine_M.ox" "rig:volumeBlendSpineBlendTwo_M.i[1]";
connectAttr "rig:IKmessureDivLeg_L.ox" "rig:volume1OverLeg_L.i2x";
connectAttr "rig:volume1OverLeg_L.ox" "rig:volumepowLeg_L.i1x";
connectAttr "rig:multWithStretchyLeg_L.ox" "rig:volumeBlendLegBlendTwo_L.ab";
connectAttr "rig:volumepowLeg_L.ox" "rig:volumeBlendLegBlendTwo_L.i[1]";
connectAttr "rig:IKmessureDivArm_L.ox" "rig:volume1OverArm_L.i2x";
connectAttr "rig:volume1OverArm_L.ox" "rig:volumepowArm_L.i1x";
connectAttr "rig:multWithStretchyArm_L.ox" "rig:volumeBlendArmBlendTwo_L.ab";
connectAttr "rig:volumepowArm_L.ox" "rig:volumeBlendArmBlendTwo_L.i[1]";
connectAttr "rig:volumeBlendSpineBlendTwo_M.o" "rig:IKSquashDistributNormalizerASpine2_M.i1[0]"
		;
connectAttr "rig:IKSquashDistributerSpine2_M.ox" "rig:IKSquashDistributNormalizerBSpine2_M.i1[0]"
		;
connectAttr "rig:IKSquashDistributNormalizerASpine2_M.o1" "rig:IKSquashDistributerSpine2_M.i1x"
		;
connectAttr "rig:volumeBlendSpineBlendTwo_M.o" "rig:IKSquashDistributNormalizerASpine1_M.i1[0]"
		;
connectAttr "rig:IKSquashDistributerSpine1_M.ox" "rig:IKSquashDistributNormalizerBSpine1_M.i1[0]"
		;
connectAttr "rig:IKSquashDistributNormalizerASpine1_M.o1" "rig:IKSquashDistributerSpine1_M.i1x"
		;
connectAttr "rig:volumeBlendSpineBlendTwo_M.o" "rig:IKSquashDistributNormalizerARootPart2_M.i1[0]"
		;
connectAttr "rig:IKSquashDistributerRootPart2_M.ox" "rig:IKSquashDistributNormalizerBRootPart2_M.i1[0]"
		;
connectAttr "rig:IKSquashDistributNormalizerARootPart2_M.o1" "rig:IKSquashDistributerRootPart2_M.i1x"
		;
connectAttr "rig:volumeBlendSpineBlendTwo_M.o" "rig:IKSquashDistributNormalizerARootPart1_M.i1[0]"
		;
connectAttr "rig:IKSquashDistributerRootPart1_M.ox" "rig:IKSquashDistributNormalizerBRootPart1_M.i1[0]"
		;
connectAttr "rig:IKSquashDistributNormalizerARootPart1_M.o1" "rig:IKSquashDistributerRootPart1_M.i1x"
		;
connectAttr "layerManager.dli[1]" "rig:Geo.id";
connectAttr "rig:renderLayerManager1.rlmi[0]" "rig:defaultRenderLayer1.rlid";
connectAttr "rig:eyes_white.oc" "rig:eyes_defaultMat.ss";
connectAttr "rig:eyes_defaultMat.msg" "rig:eyes_materialInfo1.sg";
connectAttr "rig:eyes_white.msg" "rig:eyes_materialInfo1.m";
connectAttr "rig:body_mtl.oc" "rig:lambert2SG.ss";
connectAttr "rig:lambert2SG.msg" "rig:materialInfo3.sg";
connectAttr "rig:body_mtl.msg" "rig:materialInfo3.m";
connectAttr "rig:bikini_mtl.oc" "rig:lambert3SG.ss";
connectAttr "rig:lambert3SG.msg" "rig:materialInfo4.sg";
connectAttr "rig:bikini_mtl.msg" "rig:materialInfo4.m";
connectAttr "rig:eye_blue.oc" "rig:blinn2SG.ss";
connectAttr "rig:blinn2SG.msg" "rig:materialInfo5.sg";
connectAttr "rig:eye_blue.msg" "rig:materialInfo5.m";
connectAttr "rig:iris_mtl.oc" "rig:surfaceShader1SG.ss";
connectAttr "rig:surfaceShader1SG.msg" "rig:materialInfo6.sg";
connectAttr "rig:iris_mtl.msg" "rig:materialInfo6.m";
connectAttr "rig:iris_mtl.msg" "rig:materialInfo6.t" -na;
connectAttr "rig:eye_black.oc" "rig:blinn3SG.ss";
connectAttr "rig:blinn3SG.msg" "rig:materialInfo7.sg";
connectAttr "rig:eye_black.msg" "rig:materialInfo7.m";
connectAttr "rig:teeth_mtl.oc" "rig:blinn4SG.ss";
connectAttr "rig:blinn4SG.msg" "rig:materialInfo8.sg";
connectAttr "rig:teeth_mtl.msg" "rig:materialInfo8.m";
connectAttr "rig:gum_mtl.oc" "rig:blinn5SG.ss";
connectAttr "rig:blinn5SG.msg" "rig:materialInfo9.sg";
connectAttr "rig:gum_mtl.msg" "rig:materialInfo9.m";
connectAttr "rig:lens_mtl.oc" "rig:blinn6SG.ss";
connectAttr "rig:blinn6SG.msg" "rig:materialInfo10.sg";
connectAttr "rig:lens_mtl.msg" "rig:materialInfo10.m";
connectAttr "rig:asRed.oc" "rig:asRedSG.ss";
connectAttr "rig:asRedSG.msg" "rig:materialInfo11.sg";
connectAttr "rig:asRed.msg" "rig:materialInfo11.m";
connectAttr "rig:asRed2.oc" "rig:asRed2SG.ss";
connectAttr "rig:asRed2SG.msg" "rig:materialInfo12.sg";
connectAttr "rig:asRed2.msg" "rig:materialInfo12.m";
connectAttr "rig:asGreen.oc" "rig:asGreenSG.ss";
connectAttr "rig:asGreenSG.msg" "rig:materialInfo13.sg";
connectAttr "rig:asGreen.msg" "rig:materialInfo13.m";
connectAttr "rig:asGreen2.oc" "rig:asGreen2SG.ss";
connectAttr "rig:asGreen2SG.msg" "rig:materialInfo14.sg";
connectAttr "rig:asGreen2.msg" "rig:materialInfo14.m";
connectAttr "rig:asBlue.oc" "rig:asBlueSG.ss";
connectAttr "rig:asBlueSG.msg" "rig:materialInfo15.sg";
connectAttr "rig:asBlue.msg" "rig:materialInfo15.m";
connectAttr "rig:asBlue2.oc" "rig:asBlue2SG.ss";
connectAttr "rig:asBlue2SG.msg" "rig:materialInfo16.sg";
connectAttr "rig:asBlue2.msg" "rig:materialInfo16.m";
connectAttr "rig:asWhite.oc" "rig:asWhiteSG.ss";
connectAttr "rig:asWhiteSG.msg" "rig:materialInfo17.sg";
connectAttr "rig:asWhite.msg" "rig:materialInfo17.m";
connectAttr "rig:asBlack.oc" "rig:asBlackSG.ss";
connectAttr "rig:asBlackSG.msg" "rig:materialInfo18.sg";
connectAttr "rig:asBlack.msg" "rig:materialInfo18.m";
connectAttr "rig:asBones.oc" "rig:asBonesSG.ss";
connectAttr "rig:asBonesSG.msg" "rig:materialInfo19.sg";
connectAttr "rig:asBones.msg" "rig:materialInfo19.m";
connectAttr "rig:asFaceBlue.oc" "rig:asFaceBlueSG.ss";
connectAttr "rig:asFaceBlueSG.msg" "rig:materialInfo20.sg";
connectAttr "rig:asFaceBlue.msg" "rig:materialInfo20.m";
connectAttr "rig:asFaceBrown.oc" "rig:asFaceBrownSG.ss";
connectAttr "rig:asFaceBrownSG.msg" "rig:materialInfo21.sg";
connectAttr "rig:asFaceBrown.msg" "rig:materialInfo21.m";
connectAttr "rig:asFaceGreen.oc" "rig:asFaceGreenSG.ss";
connectAttr "rig:asFaceGreenSG.msg" "rig:materialInfo22.sg";
connectAttr "rig:asFaceGreen.msg" "rig:materialInfo22.m";
connectAttr "rig:asFaceCyan.oc" "rig:asFaceCyanSG.ss";
connectAttr "rig:asFaceCyanSG.msg" "rig:materialInfo23.sg";
connectAttr "rig:asFaceCyan.msg" "rig:materialInfo23.m";
connectAttr "rig:asFaceRed.oc" "rig:asFaceRedSG.ss";
connectAttr "rig:asFaceRedSG.msg" "rig:materialInfo24.sg";
connectAttr "rig:asFaceRed.msg" "rig:materialInfo24.m";
connectAttr "layerManager.dli[2]" "rig:not_working.id";
connectAttr "rig:eyes_defaultMat.pa" ":renderPartition.st" -na;
connectAttr "rig:lambert2SG.pa" ":renderPartition.st" -na;
connectAttr "rig:lambert3SG.pa" ":renderPartition.st" -na;
connectAttr "rig:blinn2SG.pa" ":renderPartition.st" -na;
connectAttr "rig:surfaceShader1SG.pa" ":renderPartition.st" -na;
connectAttr "rig:blinn3SG.pa" ":renderPartition.st" -na;
connectAttr "rig:blinn4SG.pa" ":renderPartition.st" -na;
connectAttr "rig:blinn5SG.pa" ":renderPartition.st" -na;
connectAttr "rig:blinn6SG.pa" ":renderPartition.st" -na;
connectAttr "rig:asRedSG.pa" ":renderPartition.st" -na;
connectAttr "rig:asRed2SG.pa" ":renderPartition.st" -na;
connectAttr "rig:asGreenSG.pa" ":renderPartition.st" -na;
connectAttr "rig:asGreen2SG.pa" ":renderPartition.st" -na;
connectAttr "rig:asBlueSG.pa" ":renderPartition.st" -na;
connectAttr "rig:asBlue2SG.pa" ":renderPartition.st" -na;
connectAttr "rig:asWhiteSG.pa" ":renderPartition.st" -na;
connectAttr "rig:asBlackSG.pa" ":renderPartition.st" -na;
connectAttr "rig:asBonesSG.pa" ":renderPartition.st" -na;
connectAttr "rig:asFaceBlueSG.pa" ":renderPartition.st" -na;
connectAttr "rig:asFaceBrownSG.pa" ":renderPartition.st" -na;
connectAttr "rig:asFaceGreenSG.pa" ":renderPartition.st" -na;
connectAttr "rig:asFaceCyanSG.pa" ":renderPartition.st" -na;
connectAttr "rig:asFaceRedSG.pa" ":renderPartition.st" -na;
connectAttr "rig:eyes_white.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:body_mtl.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:bikini_mtl.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:eye_blue.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:iris_mtl.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:eye_black.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:teeth_mtl.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:gum_mtl.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:lens_mtl.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:asRed.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:asRed2.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:asGreen.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:asGreen2.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:asBlue.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:asBlue2.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:asWhite.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:asBlack.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:asBones.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:asFaceBlue.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:asFaceBrown.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:asFaceGreen.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:asFaceCyan.msg" ":defaultShaderList1.s" -na;
connectAttr "rig:asFaceRed.msg" ":defaultShaderList1.s" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "rig:defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "rig:defaultRenderLayer1.msg" ":defaultRenderingList1.r" -na;
connectAttr "rig:ikRPsolver.msg" ":ikSystem.sol" -na;
// End of rigHierachy.ma
