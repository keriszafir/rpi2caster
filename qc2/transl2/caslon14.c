/* a:\transltr\caslon14.c

float fabsoluut( float d )
int  iabsoluut( int ii )
long int labsoluut( long int li )
double dabsoluut (double db )
void cls( void)
void ontsnap(int r, int k, char b[])
void ce()       * escape-routine exit if '#' is entered *
void ask_set()
int get_line()
int NK_test ( unsigned char  c[] )
int NJ_test ( unsigned char  c[] )
int S_test  (unsigned char  c[] )
int GS2_test(unsigned char  c[])
int GS1_test(unsigned char  c[])
int GS5_test(unsigned char  c[])
int testbits( unsigned char  c[], unsigned char  nr)
int row_test (unsigned char  c[])
void setrow( unsigned char  c[],unsigned char  nr)
void stcol ( unsigned char c[], unsigned char nr )
void showbits( unsigned char  c[])
void fixed_space( void )
float gen_system(  unsigned char k,
		   unsigned char r,
		   float dikte
		)




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
"^F0^01Beknopte geschiedenis van de vitrage^00Uitvergroting van de br^01ffi^00ffl^01uidssluier filtert\015\12",
"^F0^01De_Twentse_Bank_naast_het_monument_voor_de_gevallenen.\015\012",
"en_boucl^82,_marquisette_in_slingerdraadbinding.\015\012",
"Te_onderscheiden:_polyester,_trevira,_brod^82\015\012" };


struct rec02 stcochin = {
   "Cochin Series                  ",
   5,6,7,8,9,9,9,10,10,11,12,13,14,15,18,18, /* 5 wedge... == 0 ? => 17*15 */

   12,16,20,22,24,         26, 28, 0, 0, 0,
   30,34,42,45,50 /* 49*/ ,53, 60, 0, 0, 0
} ;



struct matrijs far matrix[ 400

    /* matmax 17*16 + 50 = 322  */ ] = {

"'"   ,0, 5, 0, 2,
":"   ,2, 6, 1,15,";"   ,2, 5, 1,16,
"!"   ,2, 6, 1, 1,"?"   ,2, 9, 4, 6,
"."   ,1, 5, 0, 2,"."   ,2, 5, 0, 2,
","   ,1, 5, 0,13,","   ,2, 5, 0, 3,
"`"   ,2, 5, 0, 1,"'"   ,2, 5, 0, 0,
"`"   ,1, 5, 0, 1,"'"   ,1, 5, 0, 0,
"-"   ,1, 6, 1, 6,"-"   ,2, 6, 1, 6,
""  ,1, 9, 5, 3,""  ,2, 9, 5, 3, /* "--" ontbreekt */

"---" ,1,18,14,15,"---" ,2,18,14,15,
"\256",1, 7, 2, 2,"\257",1, 9, 2, 2,
"\256",2, 7, 2, 2,"\257",2, 7, 2, 2,

"/"   ,0, 6, 1, 2,
"\226",1, 7, 2, 0,

"6"   ,1, 9, 4, 0,"5"   ,1, 9, 4, 1,
"4"   ,1, 9, 4, 2,"3"   ,1, 9, 4, 3,"2"   ,1, 9, 4, 4,
"0"   ,1, 9, 5, 0,"9"   ,1, 9, 5, 1,"8"   ,1, 9, 5, 2,
"7"   ,1, 9, 5, 3,
"*"   ,0,10, 6, 0,
"\226",0,10, 7, 0,


"'"   ,0, 5, 0, 0,"`"   ,0, 5, 0, 1,"."   ,0, 5, 0, 2,","   ,0, 5, 0, 3,
"\214",0, 5, 0, 4,"\223",1, 5, 0, 5,"j"   ,0, 5, 0, 6,"i"   ,0, 5, 0, 7,
" "   ,0, 5, 0, 8,"l"   ,0, 5, 0, 9,"i"   ,1, 5, 0,10,"l"   ,1, 5, 0,11,
"t"   ,1, 5, 0,12,","   ,1, 5, 0,13,"\214",1, 5, 0,14,"\207",1, 6, 0,15,
"!"   ,1, 5, 0,16,



							   /* 1 */

"z"   ,2, 8, 1, 0,"!"   ,0, 6, 1, 1,"i"   ,2, 6, 1, 2,"l"   ,2, 6, 1, 3,
"("   ,0, 6, 1, 4,")"   ,0, 6, 1, 5,"-"   ,0, 6, 1, 6,"f"   ,0, 6, 1, 7,
" "   ,1, 6, 1, 8,"t"   ,0, 6, 1, 9,"s"   ,1, 6, 1,10,"c"   ,1, 6, 1,11,
"f"   ,1, 6, 1,12,"\207",0, 8, 1,13,"j"   ,1, 6, 1,14,":"   ,0, 6, 1,15,
";"   ,0, 6, 1,16,

"j"   ,2, 7, 2, 0,"s"   ,2, 7, 2, 1,"\256",0, 7, 2, 2,"\257",0, 7, 2, 3,
"r"   ,0, 7, 2, 4,"s"   ,0, 7, 2, 5,"y"   ,1, 7, 2, 6,"e"   ,1, 7, 2, 7,
"0"   ,1, 7, 2, 8,"r"   ,1, 7, 2, 9,"\224",1, 7, 2,10,"\202",1, 7, 2,11,
"\212",1, 7, 2,12,"\210",1, 7, 2,13,"I"   ,1, 7, 2,14,":"   ,1, 6, 2,15,
";"   ,1, 7, 2,16,

"\203",0, 8, 3, 0,"\205",0, 8, 3, 1,"f"   ,2, 8, 3, 2,"e"   ,2, 8, 3, 3,
"I"   ,0, 8, 3, 4,"\204",0, 8, 3, 5,"c"   ,0, 8, 3, 6,"a"   ,0, 8, 3, 7,
"e"   ,0, 8, 3, 8,"\202",0, 8, 3, 9,"\212",0, 8, 3,10,"\210",0, 8, 3,11,
"g"   ,1, 8, 3,12,"b"   ,1, 8, 3,13,"q"   ,1, 8, 3,14,"k"   ,1, 8, 3,15,
"x"   ,1, 8, 3,16,

"\204",2, 9, 4, 0,"y"   ,2, 9, 4, 1,"b"   ,2, 9, 4, 2,"c"   ,2, 9, 4, 3,
"a"   ,2, 9, 4, 4,"1"   ,1, 9, 4, 5,"?"   ,0, 9, 4, 6,"v"   ,0, 9, 4, 7,
" "   ,3, 9, 4, 8,"\224",0, 9, 4, 9,"J"   ,0, 9, 4,10,"p"   ,1, 9, 4,11,
"n"   ,1, 9, 4,12,"\201",1, 9, 4,13,"\204",1, 9, 4,14,"\205",1, 9, 4,15,
"\203",1, 9, 4,16,

"x"   ,2, 7, 5, 0,"v"   ,2, 7, 5, 1,"p"   ,2, 9, 5, 2,"t"   ,2, 9, 5, 3,
"?"   ,1, 9, 5, 4,"\227",1, 9, 5, 5,"\223",0, 9, 5, 6,"x"   ,0, 9, 5, 7,
"o"   ,0, 9, 5, 8,"z"   ,0, 9, 5, 9,"a"   ,1, 9, 5,10,"u"   ,1, 9, 5,11,
"d"   ,1, 9, 5,12,"h"   ,1, 9, 5,13,"\341",1, 9, 5,14,"fi"  ,1, 9, 5,15,
"fl"  ,1, 9, 5,16,

"q"   ,2,10, 6, 0,"r"   ,2,10, 6, 1,"o"   ,2,10, 6, 2,"3"   ,0,10, 6, 3,
"6"   ,0,10, 6, 4,"9"   ,0,10, 6, 5,"8"   ,0,10, 6, 6,"5"   ,0,10, 6, 7,
"y"   ,0, 9, 6, 8,"g"   ,0,10, 6, 9,"q"   ,0,10, 6,10,"b"   ,0,10, 6,11,
"h"   ,0,10, 6,12,"fi"  ,0,10, 6,13,"fl"  ,0,10, 6,14,"v"   ,1,10, 6,15,
"z"   ,1,10, 6,16,

"\224",2,10, 7, 0,"G"   ,2,10, 7, 1,"."   ,4,10, 7, 2,"7"   ,0,10, 7, 3,
"4"   ,0,10, 7, 4,"1"   ,0,10, 7, 5,"0"   ,0,10, 7, 6,"2"   ,0,10, 7, 7,
"u"   ,0,10, 7, 8,"n"   ,0,10, 7, 9,"p"   ,0,10, 7,10,"d"   ,1,10, 7,11,
"k"   ,0,10, 7,12,"\201",0,10, 7,13,"\341",0,10, 7,14,"S"   ,0,10, 7,15,
"\227",0,10, 7,16,
/*
~!@#$%^&*()_+
`1234567890-=
QWERTYUIOP{}|
qwertyuiop[]\
ASDFGHJKL:"
asdfghjkl;'
|ZXCVBNM<>?
\zxcvbnm,./
*/
""    ,0,11, 8, 0,""    ,0,11, 8, 1,""    ,0,11, 8, 2,"\201",2,11, 8, 3,
"k"   ,2,11, 8, 4,"d"   ,2,11, 8, 5,"n"   ,2,11, 8, 6,"u"   ,2,11, 8, 7,
"ff"  ,0,11, 8, 8,"ff"  ,1,11, 8, 9,""    ,0,11, 8,10,"S"   ,1,11, 8,11,
"J"   ,1,11, 8,12,"F"   ,1,11, 8,13,""    ,0,11, 8,14,""    ,0,11, 8,15,
""    ,0,11, 8,16,

""    ,0,12, 9, 0,""    ,0,12, 9, 1,""    ,0,12, 9, 2,"h"   ,2,12, 9, 3,
"B"   ,0,12, 9, 4,"F"   ,0,12, 9, 5,"P"   ,0,12, 9, 6,""    ,0,12, 9, 7,
""    ,1,12, 9, 8,"C"   ,1,12, 9, 9,"T"   ,1,12, 9,10,"V"   ,1,12, 9,11,
""    ,0,12, 9,12,""    ,0,12, 9,13,""    ,0,12, 9,14,""    ,0,12, 9,15,
""    ,0,12, 9,16,

""    ,0,13,10, 0,""    ,0,13,10, 1,"w"   ,2,13,10, 2,"m"   ,2,13,10, 3,
"Z"   ,0,13,10, 4,"V"   ,0,13,10, 5,"L"   ,0,13,10, 6,"C"   ,0,13,10, 7,
"w"   ,0,13,10, 8,"m"   ,1,13,10, 9,"E"   ,1,13,10,10,"A"   ,1,13,10,11,
"R"   ,1,13,10,12,"B"   ,1,13,10,13,"P"   ,1,14,10,14,"\216",1,13,10,15,
"\232",1,13,10,16,

"\216",0,14,11, 0,""    ,0,14,11, 1,"K"   ,0,14,11, 2,"Y"   ,0,14,11, 3,
"G"   ,0,14,11, 4,"T"   ,0,14,11, 5,"R"   ,0,14,11, 6,"A"   ,0,14,11, 7,
"E"   ,0,14,11, 8,"w"   ,1,14,11, 9,"U"   ,1,14,11,10,"G"   ,1,14,11,11,
"L"   ,1,14,11,12,"Y"   ,1,14,11,13,"K"   ,1,14,11,14,"Z"   ,1,14,11,15,
""    ,0,14,11,16,

""    ,0,15,12, 0,"\231",0,15,12, 1,"X"   ,0,15,12, 2,"Q"   ,0,15,12, 3,
"D"   ,0,15,12, 4,"N"   ,0,15,12, 5,""    ,0,15,12, 6,"O"   ,0,15,12, 7,
"m"   ,0,15,12, 8,"O"   ,1,13,12, 9,"N"   ,1,15,12,10,"D"   ,1,15,12,11,
"H"   ,1,15,12,12,"Q"   ,1,15,12,13,"X"   ,1,15,12,14,""    ,0,15,12,15,
"\231",1,15,12,16,

""    ,0,17,13, 0,""    ,0,17,13, 1,""    ,0,17,13, 2,""    ,1,17,13, 3,
""    ,0,17,13, 4,"1\2" ,0,17,13, 5,"\350",0,17,13, 6,""    ,0,17,13, 7,
""    ,0,17,13, 8,"H"   ,0,17,13, 9,"&"   ,0,17,13,10,"M"   ,0,17,13,11,
""    ,0,17,13,12,"%"   ,0,17,13,13,"+"   ,0,17,13,14,"#"   ,0,17,13,15,
"="   ,0,17,13,16,

""    ,0,20,14, 0,""    ,0,20,14, 1,""    ,0,20,14,02,""    ,0,20,14, 3,
""    ,0,20,14, 4,"W"   ,0,20,14, 5,""    ,0,20,14, 6,""    ,0,20,14, 7,
""    ,0,20,14, 8,"W"   ,1,20,14, 9,""    ,0,20,14,10,""    ,1,20,14,11,
""    ,0,20,14,12,"W"   ,1,20,14,13,"M"   ,0,20,14,14,"---" ,0,20,14,15,
" "   ,4,20,14,16

};




/*

" 34 dec 22 hex \042 octale

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

*/



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








