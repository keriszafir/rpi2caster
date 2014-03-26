/* a:\transltr\bembo011.c

plek '-' nog aanpassen naar E-3


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



struct matrijs far matrix[ 340 /*was 322 */  ] = {


/* missing accents i romein*/
"\214",0, 5, 0,16,"\213",0, 5, 0,15,
"\215",0, 5, 0, 7,"\241",0, 5, 0, 7,
/* a cursief */
"\203",1, 8, 2,11,"\204",1, 8, 3,15,"\205",1, 8, 5, 2,"\240",1, 8, 2,11,
/* e cursief */
"\210",1, 7, 2,10,"\211",1, 7, 2,11,"\212",1, 7, 2,12,"\202",1, 7, 2,13,
/* o cursief */
"\223",1, 8, 2,15,"\224",1, 8, 2,14,"\225",1, 8, 2,15,"\242",1, 8, 2,16,

"\227",0,10, 7,16, /*u` mist.... u" */

/* missing accents u^" cursief  */
"\226",1, 9, 5, 3,"\201",1, 9, 5, 3,
"\227",1, 9, 5,11,"\243",1, 9, 5,16,
"\214",1, 5, 0, 4,/* ... i^ */
"\267",0,14,11,14, /*^b7*/



"j"   ,2, 5, 0, 0,"/"   ,0, 5, 0, 1,"f"   ,1, 5, 0, 2,
"j"   ,1, 5, 0, 3,"i"   ,1, 5, 0, 4,"t"   ,1, 5, 0, 5,
"l"   ,1, 5, 0, 6,"i"   ,0, 5, 0, 7," "   ,0, 5, 0, 8,
"j"   ,0, 5, 0, 9,"."   ,0, 5, 0,10,","   ,0, 5, 0,11,
"'"   ,0, 5, 0,12,"l"   ,0, 5, 0,13,";"   ,0, 5, 0,14,
"\213",0, 5, 0,15,/* ?? */ "\214",0, 5, 0,16,

"i"   ,2, 6, 1, 0,""    ,0, 6, 1, 1,"r"   ,1, 6, 1, 2,
"s"   ,1, 6, 1, 3,"I"   ,0, 6, 1, 4,"J"   ,0, 6, 1, 5,
":"   ,1, 7, 1, 6,"t"   ,0, 6, 1, 7," "   ,1, 6, 1, 8,

"s"   ,0, 6, 1, 9,"f"   ,0, 6, 1,10,"("   ,0, 6, 1,11,
":"   ,0, 5, 1,12,"\210",1, 7, 1,13,"\214",1, 5, 1,14,
"`"   ,0, 6, 1,15,"c"   ,1, 6, 1,16,

"f"   ,2, 7, 2, 0,"s"   ,2, 7, 2, 1,"J"   ,1, 7, 2, 2,
"I"   ,1, 7, 2, 3,"!"   ,1, 7, 2, 4,"e"   ,1, 7, 2, 5,
"-"   ,0, 7, 2, 6,";"   ,1, 7, 2, 7,"r"   ,0, 7, 2, 8,
"!"   ,0, 7, 2, 9,")"   ,0, 6, 2,10,"\211",1, 7, 2,11,
"\212",1, 7, 2,12,"\202",1, 7, 2,13,"\224",1, 8, 2,14,
"("   ,1, 7, 2,15,")"   ,1, 7, 2,16,

"p"   ,2, 8, 3, 0,"l"   ,2, 8, 3, 1,"a"   ,1, 8, 3, 2,
"q"   ,1, 8, 3, 3,"b"   ,1, 8, 3, 4,"g"   ,1, 8, 3, 5,
"d"   ,1, 8, 3, 6,"\212",0, 8, 3, 7,"o"   ,1, 8, 3, 8,
"e"   ,0, 8, 3, 9,"a"   ,0, 8, 3,10,"c"   ,0, 8, 3,11,
"z"   ,0, 8, 3,12,"\204",0, 8, 3,13,"\210",0, 8, 3,14,
"\204",1, 8, 3,15,"\202",0, 8, 3,16,

"b"   ,2, 9, 4, 0,"1"   ,0, 9, 4, 1,"3"   ,0, 9, 4, 2,
"7"   ,0, 9, 4, 3,"y"   ,1, 9, 4, 4,"p"   ,1, 9, 4, 5,
"h"   ,1, 9, 4, 6,"n"   ,1, 9, 4, 7," "   ,2, 9, 4, 8,
"\211",0, 8, 4, 9,"6"   ,0, 9, 4,10,"9"   ,0, 9, 4,11,
"5"   ,0, 9, 4,12,"8"   ,0, 9, 4,13,"\257",0, 9, 4,14,
"\256",0, 9, 4,15,"--"  ,0, 9, 4,16,

"z"   ,2, 9, 5, 0,"t"   ,2, 9, 5, 1,"\205",1, 9, 5, 2,
"\226",1, 9, 5, 3,"v"   ,1, 9, 5, 4,"u"   ,1, 9, 5, 5,
"k"   ,1, 9, 5, 6,"\205",0, 8, 5, 7,"\207",0, 9, 5, 8,/* c-cedile ^87 */
"\203",0, 9, 5, 9,"4"   ,0, 9, 5,10,"\227",1, 9, 5,11,
"0"   ,0, 9, 5,12,"2"   ,0, 9, 5,13,"?"   ,0, 9, 5,14,
"?"   ,1,10, 5,15,"\240",0, 9, 5,16,

"y"   ,2,10, 6, 0,"v"   ,2,10, 6, 1,"g"   ,2,10, 6, 2,
"a"   ,2,10, 6, 3,"S"   ,1,10, 6, 4,"ff"  ,1,10, 6, 5,
"fi"  ,1,10, 6, 6,"F"   ,0,10, 6, 7,"g"   ,0,10, 6, 8,
"q"   ,0,10, 6, 9,"o"   ,0,10, 6,10,"h"   ,0,10, 6,11,
"ij"  ,0,10, 6,12,"y"   ,0,10, 6,13,"x"   ,0,10, 6,14,
"\223",0,10, 6,15,"\242",0,10, 6,16,

"k"   ,2,10, 7, 0,"c"   ,2,10, 7, 1,"fl"  ,1,10, 7, 2,
"ij"  ,1,10, 7, 3,"\224",0,10, 7, 4,"x"   ,1,10, 7, 5,
"z"   ,1,10, 7, 6,"S"   ,0,10, 7, 7,"n"   ,0,10, 7, 8,
"p"   ,0,10, 7, 9,"d"   ,0,10, 7,10,"b"   ,0,10, 7,11,
"u"   ,0,10, 7,12,"v"   ,0,10, 7,13,"k"   ,0,10, 7,14,
"fl"  ,0,10, 7,15,"\201",0,10, 7,16,

"q"   ,2,11, 8, 0,"h"   ,2,11, 8, 1,"o"   ,2,11, 8, 2,
"d"   ,2,11, 8, 3,"B"   ,1,11, 8, 4,"E"   ,1,11, 8, 5,
"ff"  ,0,11, 8, 6,"\227",0,10, 8, 7,"\226",0,10, 8, 8,
"3"   ,1, 8, 8, 9,"4"   ,1, 8, 8,10,"5"   ,1, 8, 8,11,
"6"   ,1, 8, 8,12,"7"   ,1, 8, 8,13,"8"   ,1, 8, 8,14,
"9"   ,1, 8, 8,15,"0"   ,1, 8, 8,16,

"x"   ,2,11, 9, 0,"u"   ,2,11, 9, 1,"n"   ,2,11, 9, 2,
"P"   ,1,11, 9, 3,"F"   ,1,11, 9, 4,"L"   ,1,11, 9, 5,
"P"   ,0,11, 9, 6,"L"   ,0,11, 9, 7,"E"   ,0,11, 9, 8,
"fi"  ,0,11, 9, 9,"fj"  ,0,11, 9,10,"1"   ,1, 9, 9,11,
"2"   ,1, 9, 9,12,"\227",0,10, 9,13,""    ,0,11, 9,14,
""    ,0,11, 9,15,"*"   ,0,11, 9,16,

"m"   ,2,13,10, 0,""    ,0,13,10, 1,"Y"   ,1,13,10, 2,
"X"   ,1,13,10, 3,"Z"   ,1,13,10, 4,"V"   ,1,13,10, 5,
"C"   ,1,13,10, 6,"T"   ,1,13,10, 7,"m"   ,1,13,10, 8,
"w"   ,1,13,10, 9,"T"   ,0,13,10,10,"B"   ,0,13,10,11,
"Z"   ,0,13,10,12,""    ,0,13,10,13,""    ,0,13,10,14,
"oe!" ,1,13,10,15,"]"   ,0, 9,10,16,

""    ,0,14,11, 0,""    ,0,14,11, 1,"K"   ,1,14,11, 2,
"R"   ,1,14,11, 3,"A"   ,1,14,11, 4,"ffi" ,1,14,11, 5,
"ffl" ,1,14,11, 6,"G"   ,0,14,11, 7,"A"   ,0,14,11, 8,
"C"   ,0,14,11, 9,"V"   ,0,14,11,10,"K"   ,0,14,11,11,
"Y"   ,0,14,11,12,"Q"   ,1,14,11,13,"\267",0,14,11,14, /*^b7*/
""    ,0,14,11,15,"["   ,0, 9,11,16,

""    ,0,15,12, 0,""    ,0,15,12, 1,"G"   ,1,15,12, 2,
"H"   ,1,15,12, 3,"D"   ,1,15,12, 4,"U"   ,1,15,12, 5,
"N"   ,1,15,12, 6,"w"   ,0,15,12, 7,"D"   ,0,15,12, 8,
"H"   ,0,15,12, 9,"X"   ,0,15,12,10,"ffi" ,0,15,12,11,
"ffl" ,0,15,12,12,"O"   ,1,15,12,13,""    ,0,15,12,14,
""    ,0,15,12,15,"oe!" ,0,15,12,16,

""    ,0,16,13, 0,""    ,0,16,13, 1,"Q"   ,0,16,13, 2,
"O"   ,0,16,13, 3,"U"   ,0,16,13, 4,""    ,0,16,13, 5,
"N"   ,0,16,13, 6,"m"   ,0,16,13, 7,"&"   ,0,16,13, 8,
"w"   ,2,16,13, 9,""    ,0,16,13,10,"fb"  ,1,16,13,11,
"fh"  ,1,16,13,12,"fk"  ,1,16,13,13,"fb"  ,0,16,13,14,
"fh"  ,0,16,13,15,"fk"  ,0,16,13,16,

""    ,0,18,14, 0,""    ,0,18,14, 1,""    ,0,18,14, 2,
"M"   ,0,18,14, 3,"M"   ,1,18,14, 4,"R"   ,0,17,14, 5,
"W"   ,1,20,14, 6,"*"   ,1,18,14, 7,""    ,0,18,14, 8,
"W"   ,0,20,14, 9,""    ,0,18,14,10,"="   ,0,18,14,11,
"..." ,0,21,14,12,"---" ,0,18,14,13,"+"  ,0,18,14,14,
"%"   ,0,18,14,15," "   ,4,18,14,16,



":"   ,2, 7, 1,12,";"   ,2, 7, 0,14,"!"   ,2, 6, 2, 9,
"?"   ,2, 9, 5,14,"."   ,1, 5, 0,10,"."   ,2, 5, 0,10,
","   ,1, 5, 0,11,","   ,2, 5, 0,11,"\047",2, 5, 0,12,
"`"   ,2, 5, 0, 4,"\047",1, 5, 0,12,""    ,1, 5, 0,14,
"-"   ,1, 6, 1, 6,"-"   ,2, 6, 1, 6,"--"  ,1, 9, 4,16,
"--"  ,2, 9, 4,16,"---" ,1,18,14,13,"---" ,2,18,14,13,
"\256",1, 9, 4,15,"\257",1, 9, 4,14,"\256",2, 9, 4,15,
"\257",2, 9, 4,14

    /* matmax 17*16 + 50 = 322  * ] =


~!@#$%^&*()_+
`1234567890-=
QWERTYUIOP{}|
qwertyuiop[]\
ASDFGHJKL:"
asdfghjkl;'
|ZXCVBNM<>?
\zxcvbnm,./

*/

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

	       /* printf("first branche \n"); */

	       for (gen_i=2;gen_i<4; gen_i++) {
		  gn_cc[gen_i] = rijcode[r-1][gen_i];
	       }

	       if (dikte != wig[r]) {
		  gn_cc[1] |= 0x08 ;  /* D */
	       }
	       gegoten_dikte += dikte;
	       cbuff[4] |= 0xff;
	   } else {

	       /* printf("second branche \n"); */

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

	   } /* at this point the desired width is less than 5 units
		this can be done with the adjustment wedges

	   */
	   if ( (central.adding > 0) && (dikte == (wig[r] + central.adding) )) {
	       /* use unit adding spatieer-wig */
	       gn_cc[1] |= 0x04 ;         /* g = 0x 00 04 00 00 */
	       gegoten_dikte += central.adding ;

	   } else {  /* aanspatieren */

	       /* printf(" using D10 & D11 wedges \n");*/

	       gn_delta = dikte - wig[r] ;
	       adjust ( wig[r], gn_delta);

	       if (central.adding > 0) {  /* unit adding on */

		  /* printf("unit adding on "); getchar();   */

		  cbuff[genbufteller+ 4]  = 0x48; /* Nk big wedge */
		  cbuff[genbufteller+ 5]  = 0x04; /* g = pump on */
		  cbuff[genbufteller+ 6]  = rijcode[uitvul[0]-1][2];
		  cbuff[genbufteller+ 7]  = rijcode[uitvul[0]-1][3];

		  cbuff[genbufteller+ 8]  = 0x44; /* NJ big wedge */
		  cbuff[genbufteller+10]  = rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11]  = rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01; /*   k = pump off */
		  cbuff[genbufteller+12]  = 0xff;

	       } else {  /* printf("unit adding off "); getchar(); */

		  cbuff[genbufteller+ 4]  = 0x48;      /* NK */
		  cbuff[genbufteller+ 5]  = 0x04;      /* g  pump on */
		  cbuff[genbufteller+ 6]  = rijcode[uitvul[0]-1][2];
		  cbuff[genbufteller+ 7]  = rijcode[uitvul[0]-1][3];

		  cbuff[genbufteller+ 8]  = 0x44;      /* NJ */
		  cbuff[genbufteller+10]  = rijcode[uitvul[1] -1][2];
		  cbuff[genbufteller+11]  = rijcode[uitvul[1] -1][3];
		  cbuff[genbufteller+11] |= 0x01;      /* k  pump off */
		  cbuff[genbufteller+12]  = 0xff;
	       }
	       genbufteller += 8;
	       for (gen_i=2;gen_i<4; gen_i++)
		  gn_cc[gen_i] = rijcode[r][gen_i];
	       gn_cc[1] |= 0x20 ;    /* S on */
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
		   case 16 : gn_cc[0]  = 0x61; break; /* HMN */
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
		   case 16 : gn_cc[0]  = 0x68; break; /* NMK   */
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
    printf(" total = %4d ", gn_ccpos + genbufteller + 4 - gn_hspi*4 );
    ce();
       */
    gegoten_dikte *= ( (float) central.set ) /5184. ;

    return(gegoten_dikte);


}   /* end gen_system  */









      ss
