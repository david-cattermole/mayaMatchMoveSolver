//Maya ASCII 2017ff05 scene
//Name: controller_create_dense_one_keyframe.ma
//Last modified: Sun, Oct 06, 2019 01:42:01 PM
//Codeset: UTF-8
requires maya "2017ff05";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2017";
fileInfo "version" "2017";
fileInfo "cutIdentifier" "201710312130-1018716";
fileInfo "osv" "Linux 3.10.0-957.27.2.el7.x86_64 #1 SMP Mon Jul 29 17:46:05 UTC 2019 x86_64";
createNode transform -s -n "persp";
	rename -uid "4A57A740-0000-649C-5D99-E11900001812";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 28 21 28 ;
	setAttr ".r" -type "double3" -27.938352729602379 44.999999999999972 -5.172681101354183e-14 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "4A57A740-0000-649C-5D99-E11900001813";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 44.82186966202994;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "4A57A740-0000-649C-5D99-E11900001814";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "4A57A740-0000-649C-5D99-E11900001815";
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
	rename -uid "4A57A740-0000-649C-5D99-E11900001816";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "4A57A740-0000-649C-5D99-E11900001817";
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
	rename -uid "4A57A740-0000-649C-5D99-E11900001818";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "4A57A740-0000-649C-5D99-E11900001819";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "transform1";
	rename -uid "4A57A740-0000-649C-5D99-E11900001821";
createNode pointConstraint -n "transform1_pointConstraint1" -p "transform1";
	rename -uid "4A57A740-0000-649C-5D99-E11900001830";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "transform1_CTRLW0" -dv 1 -min 0 -at "double";
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
	setAttr ".rst" -type "double3" 10 20 30 ;
	setAttr -k on ".w0";
createNode orientConstraint -n "transform1_orientConstraint1" -p "transform1";
	rename -uid "4A57A740-0000-649C-5D99-E11900001831";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "transform1_CTRLW0" -dv 1 -min 0 -at "double";
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
createNode scaleConstraint -n "transform1_scaleConstraint1" -p "transform1";
	rename -uid "4A57A740-0000-649C-5D99-E11900001832";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "transform1_CTRLW0" -dv 1 -min 0 -at "double";
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
createNode transform -n "transform1_CTRL";
	rename -uid "4A57A740-0000-649C-5D99-E11900001825";
createNode locator -n "locatorShape1" -p "transform1_CTRL";
	rename -uid "4A57A740-0000-649C-5D99-E11900001826";
	setAttr -k off ".v";
createNode lightLinker -s -n "lightLinker1";
	rename -uid "4A57A740-0000-649C-5D99-E1190000181A";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "4A57A740-0000-649C-5D99-E1190000181B";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "4A57A740-0000-649C-5D99-E1190000181C";
createNode displayLayerManager -n "layerManager";
	rename -uid "4A57A740-0000-649C-5D99-E1190000181D";
createNode displayLayer -n "defaultLayer";
	rename -uid "4A57A740-0000-649C-5D99-E1190000181E";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "4A57A740-0000-649C-5D99-E1190000181F";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "4A57A740-0000-649C-5D99-E11900001820";
	setAttr ".g" yes;
createNode animCurveTL -n "transform1_CTRL_translateX";
	rename -uid "4A57A740-0000-649C-5D99-E11900001827";
	setAttr ".tan" 9;
	setAttr -s 200 ".ktv[0:199]"  1 10 2 10 3 10 4 10 5 10 6 10 7 10 8 10
		 9 10 10 10 11 10 12 10 13 10 14 10 15 10 16 10 17 10 18 10 19 10 20 10 21 10 22 10
		 23 10 24 10 25 10 26 10 27 10 28 10 29 10 30 10 31 10 32 10 33 10 34 10 35 10 36 10
		 37 10 38 10 39 10 40 10 41 10 42 10 43 10 44 10 45 10 46 10 47 10 48 10 49 10 50 10
		 51 10 52 10 53 10 54 10 55 10 56 10 57 10 58 10 59 10 60 10 61 10 62 10 63 10 64 10
		 65 10 66 10 67 10 68 10 69 10 70 10 71 10 72 10 73 10 74 10 75 10 76 10 77 10 78 10
		 79 10 80 10 81 10 82 10 83 10 84 10 85 10 86 10 87 10 88 10 89 10 90 10 91 10 92 10
		 93 10 94 10 95 10 96 10 97 10 98 10 99 10 100 10 101 10 102 10 103 10 104 10 105 10
		 106 10 107 10 108 10 109 10 110 10 111 10 112 10 113 10 114 10 115 10 116 10 117 10
		 118 10 119 10 120 10 121 10 122 10 123 10 124 10 125 10 126 10 127 10 128 10 129 10
		 130 10 131 10 132 10 133 10 134 10 135 10 136 10 137 10 138 10 139 10 140 10 141 10
		 142 10 143 10 144 10 145 10 146 10 147 10 148 10 149 10 150 10 151 10 152 10 153 10
		 154 10 155 10 156 10 157 10 158 10 159 10 160 10 161 10 162 10 163 10 164 10 165 10
		 166 10 167 10 168 10 169 10 170 10 171 10 172 10 173 10 174 10 175 10 176 10 177 10
		 178 10 179 10 180 10 181 10 182 10 183 10 184 10 185 10 186 10 187 10 188 10 189 10
		 190 10 191 10 192 10 193 10 194 10 195 10 196 10 197 10 198 10 199 10 200 10;
createNode animCurveTL -n "transform1_CTRL_translateY";
	rename -uid "4A57A740-0000-649C-5D99-E11900001828";
	setAttr ".tan" 9;
	setAttr -s 200 ".ktv[0:199]"  1 20 2 20 3 20 4 20 5 20 6 20 7 20 8 20
		 9 20 10 20 11 20 12 20 13 20 14 20 15 20 16 20 17 20 18 20 19 20 20 20 21 20 22 20
		 23 20 24 20 25 20 26 20 27 20 28 20 29 20 30 20 31 20 32 20 33 20 34 20 35 20 36 20
		 37 20 38 20 39 20 40 20 41 20 42 20 43 20 44 20 45 20 46 20 47 20 48 20 49 20 50 20
		 51 20 52 20 53 20 54 20 55 20 56 20 57 20 58 20 59 20 60 20 61 20 62 20 63 20 64 20
		 65 20 66 20 67 20 68 20 69 20 70 20 71 20 72 20 73 20 74 20 75 20 76 20 77 20 78 20
		 79 20 80 20 81 20 82 20 83 20 84 20 85 20 86 20 87 20 88 20 89 20 90 20 91 20 92 20
		 93 20 94 20 95 20 96 20 97 20 98 20 99 20 100 20 101 20 102 20 103 20 104 20 105 20
		 106 20 107 20 108 20 109 20 110 20 111 20 112 20 113 20 114 20 115 20 116 20 117 20
		 118 20 119 20 120 20 121 20 122 20 123 20 124 20 125 20 126 20 127 20 128 20 129 20
		 130 20 131 20 132 20 133 20 134 20 135 20 136 20 137 20 138 20 139 20 140 20 141 20
		 142 20 143 20 144 20 145 20 146 20 147 20 148 20 149 20 150 20 151 20 152 20 153 20
		 154 20 155 20 156 20 157 20 158 20 159 20 160 20 161 20 162 20 163 20 164 20 165 20
		 166 20 167 20 168 20 169 20 170 20 171 20 172 20 173 20 174 20 175 20 176 20 177 20
		 178 20 179 20 180 20 181 20 182 20 183 20 184 20 185 20 186 20 187 20 188 20 189 20
		 190 20 191 20 192 20 193 20 194 20 195 20 196 20 197 20 198 20 199 20 200 20;
createNode animCurveTL -n "transform1_CTRL_translateZ";
	rename -uid "4A57A740-0000-649C-5D99-E11900001829";
	setAttr ".tan" 9;
	setAttr -s 200 ".ktv[0:199]"  1 30 2 30 3 30 4 30 5 30 6 30 7 30 8 30
		 9 30 10 30 11 30 12 30 13 30 14 30 15 30 16 30 17 30 18 30 19 30 20 30 21 30 22 30
		 23 30 24 30 25 30 26 30 27 30 28 30 29 30 30 30 31 30 32 30 33 30 34 30 35 30 36 30
		 37 30 38 30 39 30 40 30 41 30 42 30 43 30 44 30 45 30 46 30 47 30 48 30 49 30 50 30
		 51 30 52 30 53 30 54 30 55 30 56 30 57 30 58 30 59 30 60 30 61 30 62 30 63 30 64 30
		 65 30 66 30 67 30 68 30 69 30 70 30 71 30 72 30 73 30 74 30 75 30 76 30 77 30 78 30
		 79 30 80 30 81 30 82 30 83 30 84 30 85 30 86 30 87 30 88 30 89 30 90 30 91 30 92 30
		 93 30 94 30 95 30 96 30 97 30 98 30 99 30 100 30 101 30 102 30 103 30 104 30 105 30
		 106 30 107 30 108 30 109 30 110 30 111 30 112 30 113 30 114 30 115 30 116 30 117 30
		 118 30 119 30 120 30 121 30 122 30 123 30 124 30 125 30 126 30 127 30 128 30 129 30
		 130 30 131 30 132 30 133 30 134 30 135 30 136 30 137 30 138 30 139 30 140 30 141 30
		 142 30 143 30 144 30 145 30 146 30 147 30 148 30 149 30 150 30 151 30 152 30 153 30
		 154 30 155 30 156 30 157 30 158 30 159 30 160 30 161 30 162 30 163 30 164 30 165 30
		 166 30 167 30 168 30 169 30 170 30 171 30 172 30 173 30 174 30 175 30 176 30 177 30
		 178 30 179 30 180 30 181 30 182 30 183 30 184 30 185 30 186 30 187 30 188 30 189 30
		 190 30 191 30 192 30 193 30 194 30 195 30 196 30 197 30 198 30 199 30 200 30;
createNode animCurveTA -n "transform1_CTRL_rotateX";
	rename -uid "4A57A740-0000-649C-5D99-E1190000182A";
	setAttr ".tan" 9;
	setAttr -s 200 ".ktv[0:199]"  1 0 2 0 3 0 4 0 5 0 6 0 7 0 8 0 9 0 10 0
		 11 0 12 0 13 0 14 0 15 0 16 0 17 0 18 0 19 0 20 0 21 0 22 0 23 0 24 0 25 0 26 0 27 0
		 28 0 29 0 30 0 31 0 32 0 33 0 34 0 35 0 36 0 37 0 38 0 39 0 40 0 41 0 42 0 43 0 44 0
		 45 0 46 0 47 0 48 0 49 0 50 0 51 0 52 0 53 0 54 0 55 0 56 0 57 0 58 0 59 0 60 0 61 0
		 62 0 63 0 64 0 65 0 66 0 67 0 68 0 69 0 70 0 71 0 72 0 73 0 74 0 75 0 76 0 77 0 78 0
		 79 0 80 0 81 0 82 0 83 0 84 0 85 0 86 0 87 0 88 0 89 0 90 0 91 0 92 0 93 0 94 0 95 0
		 96 0 97 0 98 0 99 0 100 0 101 0 102 0 103 0 104 0 105 0 106 0 107 0 108 0 109 0 110 0
		 111 0 112 0 113 0 114 0 115 0 116 0 117 0 118 0 119 0 120 0 121 0 122 0 123 0 124 0
		 125 0 126 0 127 0 128 0 129 0 130 0 131 0 132 0 133 0 134 0 135 0 136 0 137 0 138 0
		 139 0 140 0 141 0 142 0 143 0 144 0 145 0 146 0 147 0 148 0 149 0 150 0 151 0 152 0
		 153 0 154 0 155 0 156 0 157 0 158 0 159 0 160 0 161 0 162 0 163 0 164 0 165 0 166 0
		 167 0 168 0 169 0 170 0 171 0 172 0 173 0 174 0 175 0 176 0 177 0 178 0 179 0 180 0
		 181 0 182 0 183 0 184 0 185 0 186 0 187 0 188 0 189 0 190 0 191 0 192 0 193 0 194 0
		 195 0 196 0 197 0 198 0 199 0 200 0;
createNode animCurveTA -n "transform1_CTRL_rotateY";
	rename -uid "4A57A740-0000-649C-5D99-E1190000182B";
	setAttr ".tan" 9;
	setAttr -s 200 ".ktv[0:199]"  1 0 2 0 3 0 4 0 5 0 6 0 7 0 8 0 9 0 10 0
		 11 0 12 0 13 0 14 0 15 0 16 0 17 0 18 0 19 0 20 0 21 0 22 0 23 0 24 0 25 0 26 0 27 0
		 28 0 29 0 30 0 31 0 32 0 33 0 34 0 35 0 36 0 37 0 38 0 39 0 40 0 41 0 42 0 43 0 44 0
		 45 0 46 0 47 0 48 0 49 0 50 0 51 0 52 0 53 0 54 0 55 0 56 0 57 0 58 0 59 0 60 0 61 0
		 62 0 63 0 64 0 65 0 66 0 67 0 68 0 69 0 70 0 71 0 72 0 73 0 74 0 75 0 76 0 77 0 78 0
		 79 0 80 0 81 0 82 0 83 0 84 0 85 0 86 0 87 0 88 0 89 0 90 0 91 0 92 0 93 0 94 0 95 0
		 96 0 97 0 98 0 99 0 100 0 101 0 102 0 103 0 104 0 105 0 106 0 107 0 108 0 109 0 110 0
		 111 0 112 0 113 0 114 0 115 0 116 0 117 0 118 0 119 0 120 0 121 0 122 0 123 0 124 0
		 125 0 126 0 127 0 128 0 129 0 130 0 131 0 132 0 133 0 134 0 135 0 136 0 137 0 138 0
		 139 0 140 0 141 0 142 0 143 0 144 0 145 0 146 0 147 0 148 0 149 0 150 0 151 0 152 0
		 153 0 154 0 155 0 156 0 157 0 158 0 159 0 160 0 161 0 162 0 163 0 164 0 165 0 166 0
		 167 0 168 0 169 0 170 0 171 0 172 0 173 0 174 0 175 0 176 0 177 0 178 0 179 0 180 0
		 181 0 182 0 183 0 184 0 185 0 186 0 187 0 188 0 189 0 190 0 191 0 192 0 193 0 194 0
		 195 0 196 0 197 0 198 0 199 0 200 0;
createNode animCurveTA -n "transform1_CTRL_rotateZ";
	rename -uid "4A57A740-0000-649C-5D99-E1190000182C";
	setAttr ".tan" 9;
	setAttr -s 200 ".ktv[0:199]"  1 0 2 0 3 0 4 0 5 0 6 0 7 0 8 0 9 0 10 0
		 11 0 12 0 13 0 14 0 15 0 16 0 17 0 18 0 19 0 20 0 21 0 22 0 23 0 24 0 25 0 26 0 27 0
		 28 0 29 0 30 0 31 0 32 0 33 0 34 0 35 0 36 0 37 0 38 0 39 0 40 0 41 0 42 0 43 0 44 0
		 45 0 46 0 47 0 48 0 49 0 50 0 51 0 52 0 53 0 54 0 55 0 56 0 57 0 58 0 59 0 60 0 61 0
		 62 0 63 0 64 0 65 0 66 0 67 0 68 0 69 0 70 0 71 0 72 0 73 0 74 0 75 0 76 0 77 0 78 0
		 79 0 80 0 81 0 82 0 83 0 84 0 85 0 86 0 87 0 88 0 89 0 90 0 91 0 92 0 93 0 94 0 95 0
		 96 0 97 0 98 0 99 0 100 0 101 0 102 0 103 0 104 0 105 0 106 0 107 0 108 0 109 0 110 0
		 111 0 112 0 113 0 114 0 115 0 116 0 117 0 118 0 119 0 120 0 121 0 122 0 123 0 124 0
		 125 0 126 0 127 0 128 0 129 0 130 0 131 0 132 0 133 0 134 0 135 0 136 0 137 0 138 0
		 139 0 140 0 141 0 142 0 143 0 144 0 145 0 146 0 147 0 148 0 149 0 150 0 151 0 152 0
		 153 0 154 0 155 0 156 0 157 0 158 0 159 0 160 0 161 0 162 0 163 0 164 0 165 0 166 0
		 167 0 168 0 169 0 170 0 171 0 172 0 173 0 174 0 175 0 176 0 177 0 178 0 179 0 180 0
		 181 0 182 0 183 0 184 0 185 0 186 0 187 0 188 0 189 0 190 0 191 0 192 0 193 0 194 0
		 195 0 196 0 197 0 198 0 199 0 200 0;
createNode animCurveTU -n "transform1_CTRL_scaleX";
	rename -uid "4A57A740-0000-649C-5D99-E1190000182D";
	setAttr ".tan" 9;
	setAttr -s 200 ".ktv[0:199]"  1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1 10 1
		 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1 27 1
		 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1 44 1
		 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1 61 1
		 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1
		 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1 95 1
		 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1 110 1
		 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1 121 1 122 1 123 1 124 1
		 125 1 126 1 127 1 128 1 129 1 130 1 131 1 132 1 133 1 134 1 135 1 136 1 137 1 138 1
		 139 1 140 1 141 1 142 1 143 1 144 1 145 1 146 1 147 1 148 1 149 1 150 1 151 1 152 1
		 153 1 154 1 155 1 156 1 157 1 158 1 159 1 160 1 161 1 162 1 163 1 164 1 165 1 166 1
		 167 1 168 1 169 1 170 1 171 1 172 1 173 1 174 1 175 1 176 1 177 1 178 1 179 1 180 1
		 181 1 182 1 183 1 184 1 185 1 186 1 187 1 188 1 189 1 190 1 191 1 192 1 193 1 194 1
		 195 1 196 1 197 1 198 1 199 1 200 1;
createNode animCurveTU -n "transform1_CTRL_scaleY";
	rename -uid "4A57A740-0000-649C-5D99-E1190000182E";
	setAttr ".tan" 9;
	setAttr -s 200 ".ktv[0:199]"  1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1 10 1
		 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1 27 1
		 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1 44 1
		 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1 61 1
		 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1
		 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1 95 1
		 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1 110 1
		 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1 121 1 122 1 123 1 124 1
		 125 1 126 1 127 1 128 1 129 1 130 1 131 1 132 1 133 1 134 1 135 1 136 1 137 1 138 1
		 139 1 140 1 141 1 142 1 143 1 144 1 145 1 146 1 147 1 148 1 149 1 150 1 151 1 152 1
		 153 1 154 1 155 1 156 1 157 1 158 1 159 1 160 1 161 1 162 1 163 1 164 1 165 1 166 1
		 167 1 168 1 169 1 170 1 171 1 172 1 173 1 174 1 175 1 176 1 177 1 178 1 179 1 180 1
		 181 1 182 1 183 1 184 1 185 1 186 1 187 1 188 1 189 1 190 1 191 1 192 1 193 1 194 1
		 195 1 196 1 197 1 198 1 199 1 200 1;
createNode animCurveTU -n "transform1_CTRL_scaleZ";
	rename -uid "4A57A740-0000-649C-5D99-E1190000182F";
	setAttr ".tan" 9;
	setAttr -s 200 ".ktv[0:199]"  1 1 2 1 3 1 4 1 5 1 6 1 7 1 8 1 9 1 10 1
		 11 1 12 1 13 1 14 1 15 1 16 1 17 1 18 1 19 1 20 1 21 1 22 1 23 1 24 1 25 1 26 1 27 1
		 28 1 29 1 30 1 31 1 32 1 33 1 34 1 35 1 36 1 37 1 38 1 39 1 40 1 41 1 42 1 43 1 44 1
		 45 1 46 1 47 1 48 1 49 1 50 1 51 1 52 1 53 1 54 1 55 1 56 1 57 1 58 1 59 1 60 1 61 1
		 62 1 63 1 64 1 65 1 66 1 67 1 68 1 69 1 70 1 71 1 72 1 73 1 74 1 75 1 76 1 77 1 78 1
		 79 1 80 1 81 1 82 1 83 1 84 1 85 1 86 1 87 1 88 1 89 1 90 1 91 1 92 1 93 1 94 1 95 1
		 96 1 97 1 98 1 99 1 100 1 101 1 102 1 103 1 104 1 105 1 106 1 107 1 108 1 109 1 110 1
		 111 1 112 1 113 1 114 1 115 1 116 1 117 1 118 1 119 1 120 1 121 1 122 1 123 1 124 1
		 125 1 126 1 127 1 128 1 129 1 130 1 131 1 132 1 133 1 134 1 135 1 136 1 137 1 138 1
		 139 1 140 1 141 1 142 1 143 1 144 1 145 1 146 1 147 1 148 1 149 1 150 1 151 1 152 1
		 153 1 154 1 155 1 156 1 157 1 158 1 159 1 160 1 161 1 162 1 163 1 164 1 165 1 166 1
		 167 1 168 1 169 1 170 1 171 1 172 1 173 1 174 1 175 1 176 1 177 1 178 1 179 1 180 1
		 181 1 182 1 183 1 184 1 185 1 186 1 187 1 188 1 189 1 190 1 191 1 192 1 193 1 194 1
		 195 1 196 1 197 1 198 1 199 1 200 1;
createNode script -n "uiConfigurationScriptNode";
	rename -uid "4A57A740-0000-649C-5D99-E11900001833";
	setAttr ".b" -type "string" "// Maya Mel UI Configuration File.\n// No UI generated in batch mode.\n";
	setAttr ".st" 3;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "4A57A740-0000-649C-5D99-E11900001834";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 120 -ast 1 -aet 200 ";
	setAttr ".st" 6;
select -ne :time1;
	setAttr ".o" 1;
	setAttr ".unw" 1;
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
	setAttr ".pa" 1;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
connectAttr "transform1_pointConstraint1.ctx" "transform1.tx";
connectAttr "transform1_pointConstraint1.cty" "transform1.ty";
connectAttr "transform1_pointConstraint1.ctz" "transform1.tz";
connectAttr "transform1_orientConstraint1.crx" "transform1.rx";
connectAttr "transform1_orientConstraint1.cry" "transform1.ry";
connectAttr "transform1_orientConstraint1.crz" "transform1.rz";
connectAttr "transform1_scaleConstraint1.csx" "transform1.sx";
connectAttr "transform1_scaleConstraint1.csy" "transform1.sy";
connectAttr "transform1_scaleConstraint1.csz" "transform1.sz";
connectAttr "transform1.pim" "transform1_pointConstraint1.cpim";
connectAttr "transform1.rp" "transform1_pointConstraint1.crp";
connectAttr "transform1.rpt" "transform1_pointConstraint1.crt";
connectAttr "transform1_CTRL.t" "transform1_pointConstraint1.tg[0].tt";
connectAttr "transform1_CTRL.rp" "transform1_pointConstraint1.tg[0].trp";
connectAttr "transform1_CTRL.rpt" "transform1_pointConstraint1.tg[0].trt";
connectAttr "transform1_CTRL.pm" "transform1_pointConstraint1.tg[0].tpm";
connectAttr "transform1_pointConstraint1.w0" "transform1_pointConstraint1.tg[0].tw"
		;
connectAttr "transform1.ro" "transform1_orientConstraint1.cro";
connectAttr "transform1.pim" "transform1_orientConstraint1.cpim";
connectAttr "transform1_CTRL.r" "transform1_orientConstraint1.tg[0].tr";
connectAttr "transform1_CTRL.ro" "transform1_orientConstraint1.tg[0].tro";
connectAttr "transform1_CTRL.pm" "transform1_orientConstraint1.tg[0].tpm";
connectAttr "transform1_orientConstraint1.w0" "transform1_orientConstraint1.tg[0].tw"
		;
connectAttr "transform1.pim" "transform1_scaleConstraint1.cpim";
connectAttr "transform1_CTRL.s" "transform1_scaleConstraint1.tg[0].ts";
connectAttr "transform1_CTRL.pm" "transform1_scaleConstraint1.tg[0].tpm";
connectAttr "transform1_scaleConstraint1.w0" "transform1_scaleConstraint1.tg[0].tw"
		;
connectAttr "transform1_CTRL_translateX.o" "transform1_CTRL.tx";
connectAttr "transform1_CTRL_translateY.o" "transform1_CTRL.ty";
connectAttr "transform1_CTRL_translateZ.o" "transform1_CTRL.tz";
connectAttr "transform1_CTRL_rotateX.o" "transform1_CTRL.rx";
connectAttr "transform1_CTRL_rotateY.o" "transform1_CTRL.ry";
connectAttr "transform1_CTRL_rotateZ.o" "transform1_CTRL.rz";
connectAttr "transform1_CTRL_scaleX.o" "transform1_CTRL.sx";
connectAttr "transform1_CTRL_scaleY.o" "transform1_CTRL.sy";
connectAttr "transform1_CTRL_scaleZ.o" "transform1_CTRL.sz";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
// End of controller_create_dense_one_keyframe.ma
