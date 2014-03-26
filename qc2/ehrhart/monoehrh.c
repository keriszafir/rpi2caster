/* c:\qc2\atimes\monodant.c

   dante diecase geneve

	Regular ASCII Chart (character codes 0 - 127)
000   (nul) 00 000   016  (dle) 10 020   032 sp 20 040   048 0 30 060
001   (soh) 01 001   017  (dc1) 11 021   033 !  21 041   049 1 31 061
002  (stx) 02 002   018  (dc2) 12 022   034 "  22 042   050 2 32 062
003  (etx) 03 003   019  (dc3) 13 023   035 #  23 043   051 3 33 063
004  (eot) 04 004   020  (dc4) 14 024   036 $  24 044   052 4 34 064
005  (enq) 05 005   021  (nak) 15 025   037 %  25 045   053 5 35 065
006  (ack) 06 006   022  (syn) 16 026   038 &  26 046   054 6 36 066
007  (bel) 07 007   023  (etb) 17 027   039 '  27 047   055 7 37 067
008  (bs)  08 010   024  (can) 18 030   040 (  28 050   056 8 38 070
009   (tab) 09 011   025  (em)  19 031   041 )  29 051   057 9 39 071
010   (lf)  0a 012   026   (eof) 1a 032   042 *  2a 052   058 : 3a 072
011  (vt)  0b 013   027  (esc) 1b 033   043 +  2b 053   059 ; 3b 073
012  (np)  0c 014   028  (fs)  1c 034   044 ,  2c 054   060 < 3c 074
013   (cr)  0d 015   029  (gs)  1d 035   045 -  2d 055   061 = 3d 075
014  (so)  0e 016   030  (rs)  1e 036   046 .  2e 056   062 > 3e 076
015  (si)  0f 017   031  (us)  1f 037   047 /  2f 057   063 ? 3f 077

	   Regular ASCII Chart (character codes 0 - 127)
064 @ 40 100   080 P 50 120  096 ` 60 140  112 p 70 160
065 A 41 101   081 Q 51 121  097 a 61 141  113 q 71 161
066 B 42 102   082 R 52 122  098 b 62 142  114 r 72 162
067 C 43 103   083 S 53 123  099 c 63 143  115 s 73 163
068 D 44 104   084 T 54 124  100 d 64 144  116 t 74 164
069 E 45 105   085 U 55 125  101 e 65 145  117 u 75 165
070 F 46 106   086 V 56 126  102 f 66 146  118 v 76 166
071 G 47 107   087 W 57 127  103 g 67 147  119 w 77 167
072 H 48 110   088 X 58 130  104 h 68 150  120 x 78 170
073 I 49 111   089 Y 59 131  105 i 69 151  121 y 79 171
074 J 4a 112   090 Z 5a 132  106 j 6a 152  122 z 7a 172
075 K 4b 113   091 [ 5b 133  107 k 6b 153  123 { 7b 173
076 L 4c 114   092 \ 5c 134  108 l 6c 154  124 | 7c 174
077 M 4d 115   093 ] 5d 135  109 m 6d 155  125 } 7d 175
078 N 4e 116   094 ^ 5e 136  110 n 6e 156  126 ~ 7e 176
079 O 4f 117   095 _ 5f 137  111 o 6f 157  127  7f 177



128 Ä 80 200  144 ê 90 220  160 † a0 240  176 ∞ b0 260  192 ¿ c0 300  208 – d0 320   224 ‡ e0 340 240   f0 360
129 Å 81 201  145 ë 91 221  161 ° a1 241  177 ± b1 261  193 ¡ c1 301  209 — d1 321   225 · e1 341 241 Ò  f1 361
130 Ç 82 202  146 í 92 222  162 ¢ a2 242  178 ≤ b2 262  194 ¬ c2 302  210 “ d2 322   226 ‚ e2 342 242 Ú  f2 362
131 É 83 203  147 ì 93 223  163 £ a3 243  179 ≥ b3 263  195 √ c3 303  211 ” d3 323   227 „ e3 343 243 Û  f3 363
132 Ñ 84 204  148 î 94 224  164 § a4 244  180 ¥ b4 264  196 ƒ c4 304  212 ‘ d4 324   228 ‰ e4 344 244 Ù  f4 364
133 Ö 85 205  149 ï 95 225  165 • a5 245  181 µ b5 265  197 ≈ c5 305  213 ’ d5 325   229 Â e5 345 245 ı  f5 365
134 Ü 86 206  150 ñ 96 226  166 ¶ a6 246  182 ∂ b6 266  198 ∆ c6 306  214 ÷ d6 326   230 Ê e6 346 246 ˆ  f6 366
135 á 87 207  151 ó 97 227  167 ß a7 247  183 ∑ b7 267  199 « c7 307  215 ◊ d7 327   231 Á e7 347 247 ˜  f7 367
136 à 88 210  152 ò 98 230  168 ® a8 250  184 ∏ b8 270  200 » c8 310  216 ÿ d8 330   232 Ë e8 350 248 ¯  f8 370
137 â 89 211  153 ô 99 231  169 © a9 251  185 π b9 271  201 … c9 311  217 Ÿ d9 331   233 È e9 351 249 ˘  f9 371
138 ä 8a 212  154 ö 9a 232  170 ™ aa 252  186 ∫ ba 272  202   ca 312  218 ⁄ da 332   234 Í ea 352 250 ˙  fa 372
139 ã 8b 213  155 õ 9b 233  171 ´ ab 253  187 ª bb 273  203 À cb 313  219 € db 333   235 Î eb 353 251 ˚  fb 373
140 å 8c 214  156 ú 9c 234  172 ¨ ac 254  188 º bc 274  204 Ã cc 314  220 ‹ dc 334   236 Ï ec 354 252 ¸  fc 374
141 ç 8d 215  157 ù 9d 235  173 ≠ ad 255  189 Ω bd 275  205 Õ cd 315  221 › dd 335   237 Ì ed 355 253 ˝  fd 375
142 é 8e 216  158 û 9e 236  174 Æ ae 256  190 æ be 276  206 Œ ce 316  222 ﬁ de 336   238 Ó ee 356 254 ˛  fe 376
143 è 8f 217  159 ü 9f 237  175 Ø af 257  191 ø bf 277  207 œ cf 317  223 ﬂ df 337   239 Ô ef 357 255    ff 377


128 Ä      144 ê      160 †    176 ∞    192 ¿    208 –    224 ‡   240 
129 Å      145 ë      161 °    177 ±    193 ¡    209 —    225 ·   241 Ò
130 Ç      146 í      162 ¢    178 ≤    194 ¬    210 “    226 ‚   242 Ú
131 É      147 ì      163 £    179 ≥    195 √    211 ”    227 „   243 Û
132 Ñ      148 î      164 §    180 ¥    196 ƒ    212 ‘    228 ‰   244 Ù
133 Ö      149 ï      165 •    181 µ    197 ≈    213 ’    229 Â   245 ı
134 Ü      150 ñ      166 ¶    182 ∂    198 ∆    214 ÷    230 Ê   246 ˆ
135 á      151 ó      167 ß    183 ∑    199 «    215 ◊    231 Á   247 ˜
136 à      152 ò      168 ®    184 ∏    200 »    216 ÿ    232 Ë   248 ¯
137 â      153 ô      169 ©    185 π    201 …    217 Ÿ    233 È   249 ˘
138 ä      154 ö      170 ™    186 ∫    202      218 ⁄    234 Í   250 ˙
139 ã      155 õ      171 ´    187 ª    203 À    219 €    235 Î   251 ˚
140 å      156 ú      172 ¨    188 º    204 Ã    220 ‹    236 Ï   252 ¸
141 ç      157 ù      173 ≠    189 Ω    205 Õ    221 ›    237 Ì   253 ˝
142 é      158 û      174 Æ    190 æ    206 Œ    222 ﬁ    238 Ó   254 ˛
143 è      159 ü      175 Ø    191 ø    207 œ    223 ﬂ    239 Ô   255



*/

int glc, gli;
int gllimit;



unsigned char kolcode[KOLAANTAL][4] = {
     0x42,    0,  0,   0,
     0x50,    0,  0,   0,
	0,    0,  0x80,0,
	0,    1,  0,   0,
	0,    2,  0,   0,
	0,    8,  0,   0,
	0, 0x10,  0,   0,
	0, 0x40,  0,   0,
	0, 0x80,  0,   0,
	1,    0,  0,   0,
	2,    0,  0,   0,
	4,    0,  0,   0,
	8,    0,  0,   0,
     0x10,    0,  0,   0,
     0x20,    0,  0,   0,
     0x40,    0,  0,   0,
	0,    0,  0,   0
};

unsigned char rijcode[RIJAANTAL][4] = {
       0, 0, 0x40, 0,
       0, 0, 0x20, 0,
       0, 0, 0x10, 0,
       0, 0, 0x08, 0,
       0, 0, 0x04, 0,
       0, 0,  0x2, 0,
       0, 0,  0x1, 0,
       0, 0,    0, 0x80,
       0, 0,    0, 0x40,
       0, 0,    0, 0x20,
       0, 0,    0, 0x10,
       0, 0,    0,  0x8,
       0, 0,    0,  0x4,
       0, 0,    0,  0x2,
       0, 0,    0,    0,
       0, 0,    0,    0
};


regel text[8] = {
"",
"",
"",
"" };


struct rec02 stcochin = {
   "Cochin Series                  ",
   5,6,7,8,9,9,9,10,10,11,12,13,14,15,18,18, /* 5 wedge... == 0 ? => 17*15 */

   12,16,20,22,24,         26, 28, 0, 0, 0,
   30,34,42,45,50 /* 49*/ ,53, 60, 0, 0, 0
} ;



struct matrijs far matrix[ 292 /* matmax 17*16 + 20 */ ] = {

";",0,7, 2, 5, ";",2,7, 2, 5,
":",0,7, 2, 4, ":",2,7, 2, 4,

"?", 2,8, 3, 4,
".", 1,5, 0, 5, ".", 2,5,0, 5,
",", 2,5, 0, 3,

/* 039 '  27 047   */
"\047",2,5, 0,14, "", 2,5,0,15,
"",1,5,0,5,


"-",  0, 6, 1, 6, "-",  1, 6, 1, 6, "-",  2, 6, 1, 6,
"--", 0, 9, 6, 6, "--", 2, 9, 6, 6, "--", 1, 9, 6, 6,
"---",0,18,14,15, "---",1,18,14,15, "---",2,18,14,15,



"",0,10,6, 4,


/* << >> */
"\256",  0,9, 5,12, "\257", 2,9, 6,16,
"\256",  1,9, 5,12, "\257", 1,9, 6,16,


/* "\256",2,9,1,14, "\257",2,9,1,13, */




	      /* ' 27 047 */
"`",1,5, 0, 0,  "\047",1,5, 0, 1, ",",1,5, 0, 2, "j",1,5, 0, 3, "l",1,5, 0, 4,
/* i"               i^ */
"i",1,5, 0, 5,  ".",0,5, 0, 6, ",",0,5, 0, 7, " ",0,5, 0, 8,"i",1,5, 0, 9,
			      /* i^*/           /* i" */
"l",1,6, 0,10,  "j",1,5, 0,11,  "\'",0,5, 0,12, "`",0,5, 0,13, ".",3,5, 0,14,
/*039 '  27 047 */
"i",0,5, 0,15,  "`",3,5, 0,16, /* high space at O-1 */


"(",0,6, 1, 0, ")",0,6, 1, 1, "/",0, 6,1,2, "i",2,6, 1, 3, "[",0,6, 1, 4,
"f",0,6, 1, 5, "]",0,6, 1, 6, "j",2,6, 1, 7," ",1,6, 1, 8, "t",1,6, 1, 9,
"s",1,6, 1,10, "i",3,6, 1,11, "l",3,6, 1,12,  "j",3,6, 1,13, "/",0,6, 1,14,
"(",3,6, 1,15, ")",3,7, 1,16,


"s",2,7, 2, 0, "c",1,7, 2, 1, "r",1,7, 2, 2, "e",1,7, 2, 3, "-",0,6, 2, 4,
							   /* á 87 207 */
":",0,6, 2, 5, ";",0,7, 2, 6, "f",0,7, 2, 7, "t",0,7, 2, 8, "!",0,7, 2, 9,
					     /* e^ 88 210 */  /* â 89 211 */
"f",3,7, 2,10, "t",3,7, 2,11, "I",3,5, 2,12, "-",3,7, 2,13, "!",3,7, 2,14,
/*  ä 8a 212         Ç 82 202 */
";",3,7, 2,15, ":",3,7, 2,16,

"f",2,8, 3, 0, "e",2,8, 3, 1, "z",2,8, 3, 2, "I",1,8, 3, 3, "b",1,8, 3, 4,
	  /* á 87 207 */
"q",1,8, 3, 5, "g",1,8, 3, 6, "o",1,8, 3, 7, "e",0,8, 3, 8, "r",0,8, 3, 9,
	     /*  ì 93 223  */
"s",0,8, 3,10, "z",0,8, 3,11, "J",0,8, 3,12, "J",3,8, 3,13, "I",0,8, 3,14,
"r",3,8, 3,15, "s",3,8, 3,16,

"l",2,9, 4, 0,  "r",2,9, 4, 1, "p",2,9, 4, 2, "J",1,9, 4, 3, "y",1,9, 4, 4,
			   /*  ä 8a 212 */                  /* Ç 82 202 */
"p",1,9, 4, 5, "a",1,9, 4, 6, "3",0,9, 4, 7, " ",2,9, 4, 8, "9",0,9, 4, 9,
"6",0,9, 4,10, "a",0,9, 4,11, "c",0,9, 4,12, "z",0,9, 4,13, "9",3,9, 4,14,
"6",3,9,4,15, "3",3,9,4,16,

"v", 2,9, 5, 0, "c",2,9, 5, 1, "a",2,9, 5, 2, "z",1,9, 5, 0, "v",1,9, 5, 4,
			     /* É 83 203                     Ö 85 205*/
"u", 1,9, 5, 5, "?",0,9, 5, 6, "7",0,9, 5, 7, "4",0,9, 5, 8, "1",0,9, 5, 9,
"0", 0,9, 5,10, "*",0,9, 5,11, "e",3,9, 5,12, "0",3,9, 5,13, "1",3,9, 5,14,
"4",3,9, 5,15,  "7",3,9, 5,16,

"x",2,9, 6, 0, "b",2,9, 6, 1, "t",2,9, 6, 2, "(",1,9, 6, 3, ")",1,9,6,4,
			  /* e^88 210 */
"x",1,9, 6, 5, "n",1,9, 6, 6, "2",0,9, 6, 7, "5",0,9, 6, 8, "8",0,9, 6, 9,
/* â 89 211 */
" . ",0,9, 6,10, "--",0,9, 6,11, "c",3, 9, 6,12,  "?",3,9, 6,13, "8",3,9, 6,14,
"5",3,9, 6,15, "2",3,9, 6,16,

"y",2,10, 7, 0, "fl",1,10, 7, 1, "fi",1,10, 7, 2, ":",1,10, 7, 3, ";",1,10, 7, 4,
"!",1,10, 7, 5, "?",1,10, 7, 6, "d",1,10, 7, 7, " ",0,10, 7, 8, "h",1,10, 7, 9,
"k",1,10, 7,10, "g",0,10, 7,11, "y",0,10, 7,12, "o",0,10, 7,13,"k",0,10,7, 14,
"v",0,10, 7,15, "x",0,10, 7,16,


"&",2,10, 8, 0, "q",2,10, 8, 1, "k",2,10, 8, 2, "d",2,10, 8, 3, "u",2,10, 8, 4,
			     /* ì 93 223 */
"g",2,10, 8, 5, "o",2,10, 8, 6, "b",0,10, 8, 7, "p",0,10, 8, 8, "fl",0,10, 8, 9,
	       /* ñ 96 226        Å 81 201          ó 97 227        § a4 244 */
"g",3,10, 8,10, "a",3,10, 8,11, "o",3,10,8,12, "y",3,10,8,13, "k",3,10, 8,14,
"v",3,10, 8,15, "x",3,10, 8,16,

					      /* ó 97 227 */
"ff",0,11, 9, 0, "S",0,11, 9, 1, "ff",1,11, 9, 2, "q",0,11, 9, 3, "h",0,11, 9, 4,
"P",0,11, 9, 5, "d",0,11, 9, 6, "n",0,11, 9, 7, "u",0,11, 9, 8, "fi",0,11, 9, 9,
"p",3,11, 9,10, "n",3,11, 9,11, "h",3,11, 9,12, "u",3,11, 9,13, "fi",3,11, 9,14,
"fl",3,11, 9,15, "S",3,11, 9,16,

"Z",1,12,10, 0, "F",1,12,10,1, "h",2,12,10, 2, "n",2,12,10, 3, "S",1,12,10, 4,
"P",1,12,10, 5, "L",1,12,10, 6, "E",1,12,10, 7, "d",3,12,10, 8, "q",3,12,10, 9,
"w",1,12,10,10, "b",3,12,10,11,  "",1,12,10,12, "E",3,12,10,13, "P",3,12,10,14,
"F",3,12,10,15, "Z",3,12,10,16,

"m", 2,13,11,0, "C",1,13,11,1, "R",1,13,11, 2, "T",1,13,11, 3, "Z",0,13,11, 4,
"",0,13,11, 5, "F",0,13,11, 6, "B",0,13,11, 7,   "E",0,13,11, 8, "m",1,13,11, 9,
"ff",3,13,11,10, "A",3,13,11,11, "w",0,13,11,12, "B",3,13,11,13, "L",3,13,11,14,
"V",3,13,11,15, "Y",3,13,11,16,
/* ####### */

"B",1,14,12, 0,  "X",0,14,12, 1, "&",0,14,12,2, "Y",0,14,12,3, "ffi",1,14,12, 4,
"w",2,14,12, 5,  "L",0,14,12, 6,  "R",0,14,12, 7, "A",0,14,12, 8, "C",0,14,12, 9,
"V",0,14,12,10,  "ffl",1,14,12,11,  "R",3,14,12,12, "T",3,13,12,13, "C",3,14,12,14,
"X",3,14,12,15, "&",3,14,12,16,

"V",1,15,13, 0, "G",1,15,13, 1, "Q",1,15,13, 2, "D",1,20,13, 3, "m",0,15,13, 4,
"ffl",0,15,13,5, "O",1,15,13, 6, "A",1,15,13, 7, "O",0,15,13, 8, "Q",0,15,13, 9,
"T",0,20,13, 10, "w",3,15,13,11, "N",3,15,13,12, "O",3,15,13,13,
"Q",3,15,13,14, "U",3,15,13,15, "K",3,20,13,16,

"X",1,15,14, 0, "Y",1,14,14, 1, "K",1,15,14, 2, "E",1,12,14, 3, "N",1,18,14, 4,
"U",1,15,14, 5, "D",0,15,14, 6, "G",0,15,14, 7, "ffi",0,18,14, 8, "H",0,15,14, 9,
"K",0,15,14,10, "N",0,15,14,11, "U",0,15,14,12, "D",3,15,14,13, "G",3,15,14,14,
"H",3,15,14,15, " ",4,18,14,16,



"W",1,18,15, 2, "&",1,18,15, 3, "M",1,18,15, 4, "W",0,18,15, 6, "M",0,18,15, 7,
"W",0,18,15, 14, "---",0,18,15, 16, "",0,18,15, 7, "",0,18,15, 8, "",0,18,15, 9,



"",0,5,0, 0



} ;





/* the routines fabs, labs etc.

    from the library can not be trusted to work

 */

float fabsoluut( float d )
{
   return ( d < 0. ? -d : d );
}

int  iabsoluut( int ii )
{
   return ( ii < 0  ? -ii : ii );
}

long int labsoluut( long int li )
{
   return ( li < 0 ? -li : li);
}

double dabsoluut (double db )
{
   return ( db < 0. ? - db : db );
}

void cls( void)
{
   _clearscreen( _GCLEARSCREEN );
}

void ontsnap(int r, int k, char b[])
{
    print_at( r, k, b);
    if ( '#'==getchar() ) exit(1);
}

void print_at(int rij, int kolom, char *buf)
{
     _settextposition( rij , kolom );
     _outtext( buf );
}

void ce()    /* escape-routine exit if '#' is entered */
{
   if ('#'==getchar())exit(1);
}

float ask_fset ;
int   ask_iset;

void ask_set()
{

    do {
	printf("set   = ");
	get_line();
	if (line_buffer[0] == '#') exit(1);
	ask_fset= atof(line_buffer);

    }
       while ( ask_fset < 5.5  || ask_fset > 14 );

    ask_fset = ask_fset * 4. + .25;
    ask_iset = (int) ask_fset;
    ask_fset = (float) ask_iset;
    ask_fset = ask_fset * .25;
    printf("s %4d %6.2f",ask_iset,ask_fset );
    if (getchar() == '#') exit(1);
    central.set = ask_iset;

}

int get_line()
{

   gllimit = MAX_REGELS;
   gli=0;
   while ( --gllimit > 0 && (glc=getchar()) != EOF && glc != '\n')
       line_buffer [gli++]=glc;
   if (glc == '\n')
       line_buffer[gli++] = glc;
   line_buffer[gli] = '\0';
   return ( gli );
}


/*
   testing NK: function:
	unit-adding off: turn on pump
	unit-adding on : change position wedge 0005"

   testing NJ: function:
	unit-adding off: change position wedge 0075"
	unit-adding on : line-kill
 */
int NK_test ( unsigned char  c[] )
{                    /*   N               K */
    return ( ( testbits(c,1) + testbits(c,4) ) == 2 ? 1 : 0 );
}

int NJ_test ( unsigned char  c[] )
{                    /*   N               J */
    return ( ( testbits(c,1) + testbits(c,5) ) == 2 ? 1 : 0 );
}

/*
    S-needle active ?
      activate adjustment wedges during casting space or character
*/
int S_test  (unsigned char  c[] )
{                  /*    S */
    return ( testbits(c,10) );
}


int GS2_test(unsigned char  c[])
{                 /*    G               S              2  */
   return ( (testbits(c,8) + testbits(c,10)+testbits(c,18) ) == 3 ? 1 : 0 );
}

int GS1_test(unsigned char  c[])
{                 /*    G                S              1 */
   return ( (testbits(c,8) + testbits(c,10)+testbits(c,17) ) == 3 ? 1 : 0 );
}

int GS5_test(unsigned char  c[])
{                 /*    G                S              5 */
   return ( (testbits(c,8) + testbits(c,10)+testbits(c,21) ) == 3 ? 1 : 0 );
}

/*  testbits:

       returns 1 when a specified bit is set in c[]

       input: *c = 4 byte = 32 bits char string
	      nr = char   0 - 31

*/

int testbits( unsigned char  c[], unsigned char  nr)
{
    return ( ( ( 0x80 >> (nr % 8) ) & c[nr/8] ) >= 1 ? 1 : 0 );
}

/*
      returns the (first) row-value set in s[]
 */



int row_i;

int row_test (unsigned char  c[])
{
   row_i = 16;

   while ( ( testbits(c, ++ row_i ) == 0 ) && (row_i < 31) );

   return ( row_i - RIJAANTAL);
}



/*
   set the desired bit of the row in the code
       input: row
 */
void setrow( unsigned char  c[],unsigned char  nr)
{
   if ( nr < 8 )
     c[2] |= tb[nr-1];
   else
     c[3] |= tb[nr-1];
}

void stcol ( unsigned char c[], unsigned char nr )
{
   switch (nr ) {
       case 2 : c[2] |= 0x80; break; /* A */
       case 5 :
	  if (central.syst == SHIFT )
	      c[1] |= 0x50; /* EF */
	  else
	      c[1] |= 0x08; /* D  */
	  break;
       default :
	  if ( nr > 2 && nr < 9 )
	      c[1] |= tk[nr];
	  else
	      c[0] |= tk[nr];
	  break;
   }
}



/*
  shows the code on screen
 */
int showi;

void showbits( unsigned char  c[])
{

    if (c[0] != -1) {
       for (showi=0;showi<=31;showi++) {
	   (testbits(c,showi) == 1) ? printf("%1c",tc[showi]) : printf(".");
	   if ( ( (showi-7) % 8) == 0)
	      printf(" ");
       }
    }
    for (showi=0;showi<4;showi++){
       printf(" %2x",c[showi]);
    }
    printf("\n");
}   /* showbits i */





/*
struct fspace {
    unsigned char pos;       / * row '_' space          * /
    float         wsp;       / * width in point         * /
    float         wunits;    / * width in units         * /
    unsigned char u1;        / * u1 position 0075 wedge * /
    unsigned char u2;        / * u2 position 0005 wedge * /
    unsigned char code[12];  / * code fixed space       * /
} datafix ;

    datafix stores all data about the fixed spaces, the text uses

	wsp = width in pointsizes
	width
	pos = row of the variable space i
	code = GS(row),
	NK g u1   0075 wedge    code to place the adjustment wegdes
	NJ u2 k   0005 wedge

   28 januari 2004: the routine seeks
	   the best suitable place to cast the fixed space:
	   wedges as near as possible to 3/8 position

   26 aug 2004: correcte code in datafix

 */

float fxwrow,   fxdelta, fxdd, fxmin=1000. , fxlw ;
int   fxidelta, fxfu1,  fu2, fxi;
float fxteken;
unsigned char fxrow;
unsigned char fxp[3] = { 0, 1, 4 };


void fixed_space( void )
{

    fxlw = datafix.wsp;

    for (fxi=0;fxi<12;fxi++)
	datafix.code[fxi]=0;

    datafix.code[ 1] = 0xa0; /* GS */
    datafix.code[ 4] = 0x48; /* NK */
    datafix.code[ 5] = 0x04; /* 0075 */
    datafix.code[ 8] = 0x44; /* NJ */
    datafix.code[11] = 0x01; /* 0005 */

    switch ( central.pica_cicero ) {
       case 'd' :   /* didot */
	 fxdelta = datafix.wsp * .0148 ;
	 break;
       case 'f' :   /* fournier */
	 fxdelta = datafix.wsp * .01357;
	 break;
       case 'p' :   /* pica */
	 fxdelta = datafix.wsp * .01389;
	 break;
    }
    datafix.wunits = fxdelta * 5184  / central.set;

    datafix.pos = 0;
    for (fxi=0;fxi<3;fxi++) {
       fxwrow  = wig[ fxp[fxi] ] * central.set ;
       fxwrow /= 5184 ;  /* = 4*1296 */
       fxdd = fxdelta - fxwrow;

       if ( fabsoluut(fxdd) < fabsoluut(fxmin) ) {
	  fxdd  *= 2000;
	  fxteken = (fxdd < 0) ? -1 : 1;
	  fxdd += ( fxteken * .5);
	  fxidelta = (int) fxdd;
	  fxidelta += 53;
	  if (fxidelta >= 16 ) {
	     fxmin = fxdd;
	     datafix.pos = fxi;
	  }
       }
    }
    switch (datafix.pos ) {
       case 0 :
	  datafix.code[2] = 0x40; /* GS1 */
	  break;
       case 4 :
	  datafix.code[2] = 0x04; /* GS5 */
	  break;
       default :
	  datafix.code[2] = 0x20; /* GS2 */
	  break;
    }

    fxwrow  = wig[ datafix.pos ] * central.set ;
    fxwrow /= 5184 ;  /* = 4*1296 */
    fxdelta -= fxwrow;
    fxdelta *= 2000;
    fxteken  = (fxdelta < 0) ? -1 : 1;
    fxdelta += ( fxteken * .5);
    fxidelta = (int) fxdelta;
    fxidelta += 53;

    fxfu1 = fxidelta / 15;
    fu2   = fxidelta % 15;
    if (fu2 == 0) {
       fu2+=15 ; fxfu1 --;
    }
    if (fxfu1>15) fxfu1=15;
    if (fxfu1<1)  fxfu1=1;
    /*
    printf("uitvulling %2d/%2d",fxfu1,fu2);
    ce();
     */

    datafix.u1 = fxfu1;
    datafix.u2 = fu2;

    if ( fxfu1 < 8 )
       datafix.code[6 ] |= tb[fxfu1-1];
    else
       datafix.code[7 ] |= tb[fxfu1-1];
    if ( fu2 < 8 )
       datafix.code[10] |= tb[fu2-1];
    else
       datafix.code[11] |= tb[fu2-1];
}

float  gegoten_dikte ;
unsigned char gn_cc[4];
int    genbufteller ;
int    gen_i, gn_hspi ;
float  gn_delta;
float  gn_epsi ;
int    gn_ccpos;    /* start: actual code for character in buffer */

/*
   23 aug 2004:

      bit setting replaced by adding

*/


float gen_system(  unsigned char k, /* kolom */
		   unsigned char r, /* rij   */
		   float dikte      /* width char in units */
		)

{
    gegoten_dikte = 0.;
    genbufteller = 0;
    gn_hspi=0 ;
    gn_delta = 0. ;
    gn_epsi = 0.0001;
    gn_ccpos=0;    /* start: actual code for character in buffer */
    /* initialize */
    for (gen_i=0; gen_i < 256; gen_i++) cbuff[gen_i] = 0;
    for (gen_i=0; gen_i < 4;   gen_i++) gn_cc[gen_i] = 0;

	/*
       printf("dikte = %7.2f wig %3d  ",dikte,wig[r] );
       printf(" verschil %10.7f ",fabs(dikte - 1.*wig[r]));
       printf(" kleiner %2d ", (fabs(dikte - 1.*wig[r]) < gn_epsi) ? 1 : 0 );
       if ('#'==getchar()) exit(1);
	 */
    if ( dikte ==  wig[r] ) {

	/* printf("width equal to wedge \n"); */

	if ( (central.syst == SHIFT) && (r == 15) ) {
	   gn_cc[1] = 0x08;
	} else {

	   for (gen_i=2;gen_i<4;gen_i++)
	      gn_cc[gen_i] = rijcode[r][gen_i];
	}
	       /* for (gen_i=0;gen_i<=3;gen_i++) {
		    printf(" gn_cc[%1d] = %3d ",gen_i,gn_cc[gen_i]);
		    ce();
		  }
		*/
	gegoten_dikte += dikte;
	genbufteller += 4;
	cbuff[4] = 0xff;
    } else {
	if (dikte < wig[r] ) {

	   /* printf("width smaller d %6.2f w %3d \n",dikte,wig[r]);
	      getchar();
	    */

	   if ( (r>0) && (dikte == wig[r-1]) && (central.syst == SHIFT ) ) {

	       /* printf("eerste tak \n"); */

	       for (gen_i=2;gen_i<4; gen_i++) {
		  gn_cc[gen_i] = rijcode[r-1][gen_i];
	       }

	       if (dikte != wig[r]) {
		  gn_cc[1] |= 0x08 ;  /* D */
	       }
	       gegoten_dikte += dikte;
	       cbuff[4] |= 0xff;
	   } else {

	       /* printf("tweede tak \n"); */

	       gn_delta =  dikte - wig[r] ;



	       adjust ( wig[r], gn_delta);

	       /* printf(" u1 = %2d u2 = %2d ",uitvul[0] ,uitvul[1] ); getchar(); */

	       if (central.adding > 0) {  /* unit adding on */

		  /* printf("unit adding on "); getchar();*/

		  cbuff[genbufteller+ 4] = 0x48; /* NK big wedge */
		  cbuff[genbufteller+ 6] = rijcode[uitvul[0] -1][2];
		  cbuff[genbufteller+ 5] = 0x04; /* g = pump on */
		  cbuff[genbufteller+ 7] = rijcode[uitvul[0] -1][3];

		  cbuff[genbufteller+ 8] =  0x44; /* NJ big wedge */
		  cbuff[genbufteller+10] =  rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11] =  rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01; /* k = pump off  */
		  cbuff[genbufteller+12] =  0xff;

	       } else {  /* unit adding off */

		  /* printf("unit adding off "); getchar(); */

		  cbuff[genbufteller+ 4] = 0x48; /* NK = pump on */
		  cbuff[genbufteller+ 5] |= 0x04; /* g  */
		  cbuff[genbufteller+ 6] = rijcode[uitvul[0]-1][2];
		  cbuff[genbufteller+ 7] = rijcode[uitvul[0]-1][3];

		  cbuff[genbufteller+ 8] =  0x44; /* NJ = pump off */
		  cbuff[genbufteller+10] =  rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11] =  rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01;  /* k  */
		  cbuff[genbufteller+12] =  0xff;
	       }
	       genbufteller += 8;
	       for (gen_i=2; gen_i<4 ; gen_i++) {
		  gn_cc[gen_i] +=  rijcode[r][gen_i];
	       }
	       gn_cc[1] |= 0x20 ; /* S-needle on */
	       gegoten_dikte += dikte;
	   }
	} else {
	   /*
	   print_at(5,1," width is bigger:\n add a high space \n");
	    */
	   gn_hspi = 0;
	   while ( dikte >= (wig[r] + wig[0])) {  /* add high space at: O1 */
	       /*
		print_at(6,1," add a high space ");
		if (getchar()=='#') exit(1);
		*/
	       cbuff[genbufteller  ] = 0x80; /* O   */
	       cbuff[genbufteller+2] = 0x40; /* r=1 */
	       genbufteller  += 4; /* raise genbufteller */
	       gegoten_dikte += wig[0] ;
	       dikte -= wig[0];
	       gn_ccpos +=4;
	       gn_hspi++;

	   } /* at this point desired width is less than 5 units
		this can be done with the adjustment wedges

	   */
	   if ( (central.adding > 0) && (dikte == (wig[r] + central.adding) )) {
	       /* gebruik spatieer-wig */
	       gn_cc[1] |= 0x04 ;         /* g = 0x 00 04 00 00 */
	       gegoten_dikte += central.adding ;

	   } else {  /* aanspatieren */

	       /* printf(" aanspatieren met uitvul-wiggen \n");*/

	       gn_delta = dikte - wig[r] ;
	       adjust ( wig[r], gn_delta);

	       if (central.adding > 0) {  /* unit adding on */

		  /* printf("unit adding on "); getchar();   */

		  cbuff[genbufteller+ 4] = 0x48; /* Nk big wedge */
		  cbuff[genbufteller+ 5] = 0x04; /* g = pump on */
		  cbuff[genbufteller+ 6] = rijcode[uitvul[0]-1][2];
		  cbuff[genbufteller+ 7] = rijcode[uitvul[0]-1][3];

		  cbuff[genbufteller+ 8] = 0x44; /* NJ big wedge */
		  cbuff[genbufteller+10] = rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11] = rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01; /* k = pump off */
		  cbuff[genbufteller+12] = 0xff;

	       } else {  /* unit-adding off */

		  /* printf("unit adding off "); getchar(); */

		  cbuff[genbufteller+ 4] =  0x48;      /* NK */
		  cbuff[genbufteller+ 5] =  0x04;      /* g  pump on */
		  cbuff[genbufteller+ 6] =  rijcode[uitvul[0]-1][2];
		  cbuff[genbufteller+ 7] =  rijcode[uitvul[0]-1][3];

		  cbuff[genbufteller+ 8] =  0x44;      /* NJ */
		  cbuff[genbufteller+10] =  rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11] =  rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01;      /* k  pump off */
		  cbuff[genbufteller+12] =  0xff;
	       }
	       genbufteller += 8;
	       for (gen_i=2;gen_i<4; gen_i++)
		  gn_cc[gen_i] = rijcode[r][gen_i];
	       gn_cc[1] |= 0x20 ; /* S on */
	       gegoten_dikte = dikte;
	   }
	}
    }

    /* make column code */
    if ( (central.syst == SHIFT) && ( k == 5 ) ) {

	  gn_cc[1] =  0x50; /* EF = D */
    } else {
	  /* 17*15 & 17*16 */
       for (gen_i=0; gen_i<=2; gen_i++)
	  gn_cc[gen_i] |= kolcode[k][gen_i];

       if ( r == 15) {
	  switch (central.syst ) {
	     case MNH :
		switch (k) {
		   case  0 : gn_cc[0] |= 0x01; break; /* H   */
		   case  1 : gn_cc[0] |= 0x01; break; /* H   */
		   case  9 : gn_cc[0] |= 0x40; break; /* N   */
		   case 15 : gn_cc[0] |= 0x20; break; /* M   */
		   case 16 : gn_cc[0] =  0x61; break; /* HMN */
		   default :
		      gn_cc[0] |= 0x21; break; /* NM  */
		}
		break;
	     case MNK :
		   /*
		byte 1:      byte 2:     byte 3:     byte 4:
		ONML KJIH    GFSE DgCB   A123 4567   89ab cdek
		   */
		switch (k) {
		   case  0 : gn_cc[0] |= 0x08; break; /* NI+K  */
		   case  1 : gn_cc[0] |= 0x08; break; /* NL+K  */
		   case 12 : gn_cc[0] |= 0x40; break; /* N + K */
		   case 14 : gn_cc[0] |= 0x28; break; /* K + M */
		   case 15 : gn_cc[0] |= 0x20; break; /* N + M */
		   case 16 : gn_cc[0] =  0x68; break; /* NMK   */
		   default : gn_cc[0] |= 0x28; break; /* MK  */
		}
	     break;
	  }
       }
    }

    if ((uitvul[0] == 3) && (uitvul[1]  == 8)) {

	  gn_cc[1] &=  ~0x20; /* mask bit 10 to zero */
	  cbuff[gn_ccpos + 4] = 0xff;
    }
	/* printf(" gn_ccpos = %3d ",gn_ccpos); */

    for (gen_i=0;gen_i<=3;gen_i++) {
       cbuff[gn_ccpos+gen_i] = gn_cc[gen_i]; /* fill buffer  */

		/*   printf(" gn_ccpos+gen_i %3d gn_cc[%1d] = %4d ",gn_ccpos+gen_i,gen_i,gn_cc[gen_i]);
		ce();
		*/
    }

    cbuff[gn_ccpos + genbufteller + 4 - gn_hspi*4 ] = 0xff;

    /*
    printf(" totaal = %4d ", gn_ccpos + genbufteller + 4 - gn_hspi*4 );
    ce();
       */
    gegoten_dikte *= ( (float) central.set ) /5184. ;

    return(gegoten_dikte);


}   /* end gen_system  */





/*

   reading: reads a matrix-file from disc

 */


int readp, readi, readj;

char r_eading()
{
    char reda = 0;

    /* global data concerning matrix files */

    /*
    FILE  *finmatrix ;
    size_t mat_recsize = sizeof( matfilerec );
    size_t recs2       = sizeof( cdata  );
    fpos_t *recpos, *fp;
    int  mat_handle;
    long int mat_length, mat_recseek;
    char inpathmatrix[_MAX_PATH];
    long int aantal_records;
	 / * number of records in mat_file */


    cls();

    print_at(10,10,"read matrix file ");

    readi = 0;
    do {
       print_at(13,10,"name input-file : " ); gets( inpathmatrix );
       if( ( finmatrix = fopen( inpathmatrix, "rb" )) == NULL )
       {
	  readi++;
	  if ( readi==1) {
	     print_at(15,10,"Can't open file");
	     printf(" %2d time\n",readi );
	  } else {
	     print_at(15,10,"Can't open file");
	     printf(" %2d times\n",readi );
	  }
	  if (readi == 10) return(0) ;
       }
    }
      while ( finmatrix == NULL );

    fclose(finmatrix);

    mat_handle = open( inpathmatrix,O_BINARY |O_RDONLY );

    /* Get and print mat_length. */
    mat_length = filelength( mat_handle );
    printf( "%s = %ld byte\n", inpathmatrix, mat_length );

    close(mat_handle);

    finmatrix = fopen( inpathmatrix, "rb" )   ;

    aantal_records = mat_length / mat_recsize ;

    /* global : mnumb = number of mats in the mat-case */

    printf("The file = %7d recds ",aantal_records);
    getchar();

    /*
    printf("Now the contents of the file will follow, \n");
    printf("from start to finish \n\n");
    getchar();
     */

    /* first cdata 70 bytes */
    readp =  0 * recs2 ;
    *fp = ( fpos_t ) ( readp ) ;
    fsetpos( finmatrix , fp );
    fread( &cdata, recs2 , 1, finmatrix );

    for (readi=0;readi<34;readi++)
	namestr[readi] =
	cdata.cnaam[readi] ;
    for (readi=0;readi<RIJAANTAL;readi++) wig[readi] = cdata.wedge[readi];
    nrows =
	 ( wig[15]==0 ) ? 15 : 16 ;

    readi = 0;
    for (mat_recseek = 10; mat_recseek <= aantal_records -11;
		      mat_recseek ++ ){

	    readp =  mat_recseek  * mat_recsize;
	    *fp = ( fpos_t ) ( readp ) ;
	    fsetpos( finmatrix , fp );
	    fread( &matfilerec, mat_recsize, 1, finmatrix );

	    for (readj=0;readj<3;readj++)
	       matrix[readi].lig[readj] = matfilerec.lig[readj] ;
	    matrix[readi].srt    = matfilerec.srt;
	    matrix[readi].w      = matfilerec.w  ;
	    matrix[readi].mrij   = matfilerec.mrij ;
	    matrix[readi].mkolom = matfilerec.mkolom ;

	    readi++;
    }
    fclose(finmatrix);
    reda = 1;
    return (reda );

}  /*  r_eading() : read matrix from file */







