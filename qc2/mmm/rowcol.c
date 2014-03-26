#include <bios.h>
#include <conio.h>
#include <stdio.h>
#include <graph.h>
void print_at(int r, int c, char *s);
void cls();

void print_at(int r, int c, char *s)
{
    _settextposition(r,c);
    _outtext( s );
}

void cls()
{
    _clearscreen( _GCLEARSCREEN );
}


void delay2( int tijd )
{
    long begin_tick, end_tick;
    long i;
    char c;

    _bios_timeofday( _TIME_GETCLOCK, &begin_tick);
    /* printf(" begin   = %lu \n",begin_tick);*/

    do {
       if (kbhit() ) {
	   c = getch();
	   if( c == '=' ) exit(1);
       }
       _bios_timeofday( _TIME_GETCLOCK, &end_tick);
    }
       while (end_tick < begin_tick + tijd);

    /* printf(" eind    = %lu \n",end_tick); */
    /* printf(" delta   = %lu \n",end_tick- begin_tick); */

    /* while ( end_tick = tijd + begin_tick ) ; */
}



unsigned char l[4];
char   line_buffer[80];
int    nlineb ;
int    alpha;
int    clri;
int    lrj;
int    lc1,lr1;
int    lign;

void a_b(int row, int col );
void add_buf(int row,int col, char c);
int  alphahex1 ( char c );
void clr_buf();
void r_mat ( int r );




void add_buf(int row,int col,  char c)
{
    _settextposition(row,col+nlineb );
    printf("%1c",c);
    line_buffer[nlineb++ ]= c;
}

void a_b(int row, int col )
{
    _settextposition(row,col+nlineb-1);
    printf("%1c",line_buffer[nlineb-1]);
}


int alphahex1 ( char c )
{
   alpha = 0;

   if ( c >= '0' && c <= '9' ) alpha = c - '0';
   if ( c >= 'a' && c <= 'f' ) alpha = c - 'a' + 10;

   return ( alpha );
}

void std( char c);

char stc2;

void std ( char c)
{
   line_buffer[nlineb-1]= c ;
   stc2=1;
}

int lig__get(int row, int col)
{
    char c, c1, c2 ;
    int  nn;

    clr_buf();
    print_at(row,col,"               ");
    /* time */
    do {
       _settextposition(row,col+nlineb);
       while ( ! kbhit() );
       c=getch();
       if (c==0) {
	   getch();  /* ignore function keys */
       }
       stc2=0;

       /* delay2(5); */

       switch ( c ) {
	   case  0  :
	      stc2=-1;
	      break;
	   case  8  :  /* backspace */
	      stc2 = -1;
	      if ( nlineb > 0 ) {
		 nlineb --;
		 line_buffer[nlineb]= '\0';
		 _settextposition(row,col+nlineb);
		 printf(" ");
		 _settextposition(row,col+nlineb);
	      }
	      break;
	   case 13 :
	      stc2=-1;
	      break;
	   case '-' :
	      if (nlineb > 0) {
		 switch (line_buffer[nlineb-1] ){
		     case 'd': /* 208 – d0 320 */
			std ( 0xd0 );
			break;
		     case 'D': /* 209 — d1 321 */
			std (0xd1);
			break;
		 }
	      }
	      break;
	   case '>' :
	      if (nlineb > 0) {
		 if (line_buffer[nlineb-1] == '>' ){
			std (0xae);

		 }
	      }
	      break;
	   case '<' :
	      if (nlineb > 0) {
		 if (line_buffer[nlineb-1]  == '<' ){
			std (0xaf);

		 }
	      }
	      break;
	   case 'E' :
	      if (nlineb == 1 && line_buffer[nlineb-1] == 'A' ) std (0x92);
	      break;
	   case 'e' :
	      if (nlineb == 1 && line_buffer[nlineb-1] == 'a' ) std (0x91);
	      break;
	   case 'z' :
	      if (nlineb > 0 && line_buffer[nlineb-1] == 's') std (0xe1);
	      break;
	   case '!' :
	      if (nlineb > 0) {
		 switch (line_buffer[nlineb-1] ){
		     case 'c': std (0x87); break;
		     case 'C': std (0x80); break;
		 }
	      }
	      break;
	   case ',' :
	      if (nlineb > 0) {
		 switch (line_buffer[nlineb-1] ){
		     case 'c': std (0x87); break;
		     case 'C': std (0x80); break;
		 }
	      }
	      break;
	   case '~' :
	      if ( nlineb > 0 ) {
		 switch (line_buffer[nlineb-1] ){
		     case 'n': std (0xa4); break;
		     case 'N': std (0xa5); break;
		     case 'a': std (0xc6); break;
		     case 'A': std (0xc7); break;
		 }
	      }
	      break;
	   case '"' :
	      if (nlineb > 0 ) {
		 switch (line_buffer[nlineb-1] ){
		     case 'a' : std (0x84); break;
		     case 'e' : std (0x89); break;
		     case 'i' : std (0x8b); break;
		     case 'o' : std (0x94); break;
		     case 'u' : std (0x81); break;
		     case 'A' : std (0x8e); break;
		     case 'E' : std (0xd3); break;
		     case 'I' : std (0xd8); break;
		     case 'O' : std (0x99); break;
		     case 'U' : std (0x9a); break;
		 }
	      }
	      break ;
	   case '`' :
	      if (nlineb > 0 ) {
		 switch (line_buffer[nlineb-1] ){
		     case 'a' : std (0x85); break;
		     case 'e' : std (0x8a); break;
		     case 'i' : std (0x8d); break;
		     case 'o' : std (0x95); break;
		     case 'u' : std (0x97); break;
		     case 'A' : std (0xb7); break;
		     case 'E' : std (0xd4); break;
		     case 'I' : std (0xde); break;
		     case 'O' : std (0xe3); break;
		     case 'U' : std (0xeb); break;
		 }
	      }
	      break ;
	   case '\'':
	      if (nlineb > 0 ) {
		 switch (line_buffer[nlineb-1] ){
		     case 'y' : std (0xec); break;
		     case 'Y' : std (0xed); break;
		     case 'a' : std (0xa0); break;
		     case 'e' : std (0x82); break;
		     case 'i' : std (0xa1); break;
		     case 'o' : std (0xa2); break;
		     case 'u' : std (0xa3); break;
		     case 'A' : std (0xb5); break;
		     case 'E' : std (0x90); break;
		     case 'I' : std (0xd6); break;
		     case 'O' : std (0xe0); break;
		     case 'U' : std (0xe9); break;
		 }
	      }
	      break ;
	   case '^' :
	      if (nlineb > 0 ) {
		 switch (line_buffer[nlineb-1] ){
		     case 'a' : std (0x83); break;
		     case 'e' : std (0x88); break;
		     case 'i' : std (0x8c); break;
		     case 'o' : std (0x93); break;
		     case 'u' : std (0x96); break;
		     case 'A' : std (0xb6); break;
		     case 'E' : std (0xd2); break;
		     case 'I' : std (0xd7); break;
		     case 'O' : std (0xe2); break;
		     case 'U' : std (0xea); break;
		 }
	      }
	      break ;
	   default :
	      if ( ! ( c >= 32 && c <= 127) ) {
		 c = 13;
		 stc2 = -1;
	      }
	      break;
       }
       switch(stc2 ) {
	  case 1 :
	    a_b ( row, col );
	    break;
	  case 0 :
	    add_buf( row, col, c);
	    break;
       }

    }
       while (nlineb < 5 && c != 13 );

    nn=0;
    for (c2=0;c2 < nlineb && line_buffer[c2] != '\0' ; c2 ++) nn++;
    nlineb = nn <= 3 ? nn : 3 ;

    if (nlineb == 3 )
    {
       if ( line_buffer[1] == '/' )
       {
	  switch (line_buffer[0] )
	  {
	     case '3' :
	       if (line_buffer[2]=='4')
	       {
		    line_buffer[0] = 0xf3;
		    line_buffer[1] = 0;
		    line_buffer[2] = 0;
		    nlineb = 1;
		    _settextposition(row,col);
		    printf("%1c   ",line_buffer[0]);
	       }
	       break;
	     case '1' :
	       switch (line_buffer[2] )
	       {
		  case '2' :
		    line_buffer[0] = 0xab;
		    line_buffer[1] = 0;
		    line_buffer[2] = 0;
		    nlineb = 1;
		    _settextposition(row,col);
		    printf("%1c   ",line_buffer[0]);
		    break;
		 case '4' :
		    line_buffer[0] = 0xac;
		    line_buffer[1] = 0;
		    line_buffer[2] = 0;
		    nlineb = 1;
		    _settextposition(row,col);
		    printf("%1c   ",line_buffer[0]);
		    break;
	       }
	       break;
	  }
       } else {
	  if (line_buffer[0]=='^'){
	     c  = line_buffer[1];
	     c1 = line_buffer[2];
	     nn = 16 * alphahex1( c ) +alphahex1( c1 );
	     if ( nn >= 128 ) {
		 line_buffer[0] = nn;
		 line_buffer[1] = '\0';
		 line_buffer[2] = '\0';
		 nlineb = 1;
		 _settextposition(row,col);
		 printf("     ");
		 _settextposition(row,col);
		 printf("%1c   ",line_buffer[0]);
	     }
	  }
       }
    }
    line_buffer[nlineb]='\0';

    return (nlineb);
}


int get__row(int row, int col)
{
    char c;
    int  u;

    print_at(row,col,"   ");
    _settextposition(row,col);

    do {
       while (!kbhit());
       c=getch();
       if (c==0) getch();
       if (c<'0' || c>'9') {
	   print_at(row,col," ");
	   print_at(row,col,"");
       }
    }
       while (c<'0' || c>'9');
    _settextposition(row,col);
    printf("%1c",c);

    line_buffer[nlineb++]=c;
    switch (c)
    {
       case '2' : u=1; l[2] |= 0x20; break;
       case '3' : u=2; l[2] |= 0x10; break;
       case '4' : u=3; l[2] |= 0x08; break;
       case '5' : u=4; l[2] |= 0x04; break;
       case '6' : u=5; l[2] |= 0x02; break;
       case '7' : u=6; l[2] |= 0x01; break;
       case '8' : u=7; l[3] |= 0x80; break;
       case '9' : u=8; l[3] |= 0x40; break;
       case '1' :
	  u=0;
	  print_at(row,col+1,"");
	  do {
	     while (!kbhit());
	     c=getche();
	     if (c!= 13 && c < '0' || c > '6' ) {
		print_at(row,col+1," ");
		print_at(row,col+1,"");
	     }
	  }
	     while (c!= 13 && c < '0' || c > '6' );
	  switch ( c) {
	     case 13 :
		l[2] |= 0x40;
		u = 0;
		line_buffer[nlineb++]='\0';
		break;
	     default :
		u = 9 + c - '0';
		line_buffer[nlineb++]=c;
		line_buffer[nlineb]='\0';

		switch (u) {
		   case  9 : l[3] |= 0x20; break;
		   case 10 : l[3] |= 0x10; break;
		   case 11 : l[3] |= 0x08; break;
		   case 12 : l[3] |= 0x04; break;
		   case 13 : l[3] |= 0x02; break;
		   case 14 : l[3] |= 0x00; break;
		}
		break;
	   }
	   break;
    }

    /*
    printf("u = %3d ",u);
    if (getchar()=='#') exit(1);
     */

    return (u);
}

int get__col(int row, int col)
{
    char c;
    int  u;

    print_at(row,col,"   ");
    _settextposition(row,col);

    do {
       while (!kbhit());
       c=getch();
       if (c==0) getch();

       if (c>='a' && c <='o') {
	   c += ('A' - 'a');
       }
       if (c<'A' || c>'0') {
	   print_at(row,col," ");
	   print_at(row,col,"");
       }
    }
       while (c<'A' || c>'O');
    _settextposition(row,col);
    printf("%1c",c);
    line_buffer[nlineb++]=c;
    switch (c)
    {
       case 'A' : u= 2; l[2] |= 0x80; break;
       case 'B' : u= 3; l[1] |= 0x01;break;
       case 'C' : u= 4; l[1] |= 0x02;break;
       case 'D' : u= 5; l[1] |= 0x08;break;
       case 'E' : u= 6; l[1] |= 0x10;break;
       case 'F' : u= 7; l[1] |= 0x40;break;
/* ONML KJIH  GFSE DgCB  A123 4567  89ab cdek */
       case 'G' : u= 8; l[1] |= 0x80;break;
       case 'H' : u= 9; l[0] |= 0x01;break;
       case 'I' : u=10; l[0] |= 0x02;break;
       case 'J' : u=11; l[0] |= 0x04;break;
       case 'K' : u=12; l[0] |= 0x08;break;
       case 'L' : u=13; l[0] |= 0x10;break;
       case 'M' : u=14; l[0] |= 0x20;break;

/* ONML KJIH  GFSE DgCB  A123 4567  89ab cdek */

       case 'O' : u=16; break;
       case 'N' :
	  _settextposition(row,col+1);
	  do {
	     while (!kbhit());
	     c=getche();
	     if ( c==0) getch();
	     if (c>='a' && c <='o') {
		  c += ('A' - 'a');
	     }

	     if (c!= 'I' && c!='L' && c != 13 ){
		print_at(row,col+1," ");
		_settextposition(row,col+1);
	     }
	  }
	     while (c!= 'I' && c!='L' && c != 13 );

	  _settextposition(row,col+1);
	  switch ( c) {
	     case 'I' :
		u = 0;
		l[0] |= 0x42; /* NI ONML KJIH */
		line_buffer[nlineb++]=c;
		line_buffer[nlineb]='\0';
		printf("%1c",c);

		break;
	     case 'L' :
		u = 1;
		l[0] |= 0x50; /* NL ONML KJIH */
		line_buffer[nlineb++]=c;
		line_buffer[nlineb]='\0';

		printf("%1c",c);
		break;
	     case 13 :
		u = 15;
		l[0] |= 0x40; /* N */
		line_buffer[nlineb]='\0';
		break;
	   }
	   break;
    }
    return(u);
}


void clr_buf()
{
   nlineb=0;
   for (clri=0;clri<20;clri++) line_buffer[clri]='\0';
}



void r_mat ( int r )
{
      print_at(r,1,"Read mat ");

      clr_buf();
      print_at(r,11,"Column ");
      lc1 = get__col(r,18 );
      line_buffer[nlineb++] ='-';
      printf(" row ");
      lr1 = get__row(r,25 );

      print_at(r,11,"                                     ");
      print_at(r,11,"");
      for (lrj=0; lrj < nlineb; lrj++)
	  printf("%1c",line_buffer[lrj]);

      clr_buf();
      print_at(r,15," = ");
      lign =  lig__get(r, 18);
}

main()
{
   int i,j, n ;
   i=0;
   cls();
   do {

      r_mat(24);

      print_at(2,0,"");
      printf(" r1 = %2d c1 = %2d n= %2d lig = ",lr1,lc1,lign);
      for (j=0; j<lign; j++)
	 printf("%1c",line_buffer[j]);
      if ( getchar()=='#')exit(1);
      i++;

   }
      while (i<10);
}

/*

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

243 Û  f3 363
171 ´  ab 253
172 ¨  ac 254


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

