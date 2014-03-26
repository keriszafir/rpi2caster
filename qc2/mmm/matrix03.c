    /***************************************************************
    *                                                             *
    *            matrix : manipulation with diecases              *
    *                                                             *
    *               version 0.0.3. 30 march 2006                  *
    *                                                             *
    *        John Cornelisse   computer-2-caster-project          *
    *                                                             *
    ***************************************************************

   version  28-3-2006

   bugs fixed in:

       unsigned char get__srt(int row, int col )
       int lig__get(int row, int col)
	  reading empty ligatures: clears place in diecase
	  proper counting lenght ligature
	  special characters hexadecimal input tested
	  fractions 1/2 1/4 3/4 tested
       void r_mat ( int r )
       void edit()
       void menu()

   version  29-3-2006

   bugs fixed in :

       aanvullen()
	  records not found, because buffer all[] not filled

   changed:
       vul_aan();
       wisa()

   version 30-3-2006

   added: routine input wedges
	input system
	input wedge
	input set

    */

   #include <conio.h>
   #include <stdio.h>
   #include <graph.h>
   #include <io.h>
   #include <dos.h>
   #include <stdlib.h>
   #include <string.h>

   #define  RIJAANTAL  16

   #define  NORM       0
   #define  NORM2      1

   #define  MNH        2
   #define  MNK        3
   #define  SHIFT      4

   #define  MAX_REGELS 55
   #define  FALSE      0
   #define  TRUE       1
   #define  MAXBUFF    512
   #define  HALFBUFF   256


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



   128 € 80 200  144  90 220  160   a0 240  176 ° b0 260  192 À c0 300  208 Ð d0 320   224 à e0 340 240 ð  f0 360
   129  81 201  145 ‘ 91 221  161 ¡ a1 241  177 ± b1 261  193 Á c1 301  209 Ñ d1 321   225 á e1 341 241 ñ  f1 361
   130 ‚ 82 202  146 ’ 92 222  162 ¢ a2 242  178 ² b2 262  194 Â c2 302  210 Ò d2 322   226 â e2 342 242 ò  f2 362
   131 ƒ 83 203  147 “ 93 223  163 £ a3 243  179 ³ b3 263  195 Ã c3 303  211 Ó d3 323   227 ã e3 343 243 ó  f3 363
   132 „ 84 204  148 ” 94 224  164 ¤ a4 244  180 ´ b4 264  196 Ä c4 304  212 Ô d4 324   228 ä e4 344 244 ô  f4 364
   133 … 85 205  149 • 95 225  165 ¥ a5 245  181 µ b5 265  197 Å c5 305  213 Õ d5 325   229 å e5 345 245 õ  f5 365
   134 † 86 206  150 – 96 226  166 ¦ a6 246  182 ¶ b6 266  198 Æ c6 306  214 Ö d6 326   230 æ e6 346 246 ö  f6 366
   135 ‡ 87 207  151 — 97 227  167 § a7 247  183 · b7 267  199 Ç c7 307  215 × d7 327   231 ç e7 347 247 ÷  f7 367
   136 ˆ 88 210  152 ˜ 98 230  168 ¨ a8 250  184 ¸ b8 270  200 È c8 310  216 Ø d8 330   232 è e8 350 248 ø  f8 370
   137 ‰ 89 211  153 ™ 99 231  169 © a9 251  185 ¹ b9 271  201 É c9 311  217 Ù d9 331   233 é e9 351 249 ù  f9 371
   138 Š 8a 212  154 š 9a 232  170 ª aa 252  186 º ba 272  202 Ê ca 312  218 Ú da 332   234 ê ea 352 250 ú  fa 372
   139 ‹ 8b 213  155 › 9b 233  171 « ab 253  187 » bb 273  203 Ë cb 313  219 Û db 333   235 ë eb 353 251 û  fb 373
   140 Œ 8c 214  156 œ 9c 234  172 ¬ ac 254  188 ¼ bc 274  204 Ì cc 314  220 Ü dc 334   236 ì ec 354 252 ü  fc 374
   141  8d 215  157  9d 235  173 ­ ad 255  189 ½ bd 275  205 Í cd 315  221 Ý dd 335   237 í ed 355 253 ý  fd 375
   142 Ž 8e 216  158 ž 9e 236  174 ® ae 256  190 ¾ be 276  206 Î ce 316  222 Þ de 336   238 î ee 356 254 þ  fe 376
   143  8f 217  159 Ÿ 9f 237  175 ¯ af 257  191 ¿ bf 277  207 Ï cf 317  223 ß df 337   239 ï ef 357 255    ff 377


   128 €      144       160      176 °    192 À    208 Ð    224 à   240 ð
   129       145 ‘      161 ¡    177 ±    193 Á    209 Ñ    225 á   241 ñ
   130 ‚      146 ’      162 ¢    178 ²    194 Â    210 Ò    226 â   242 ò
   131 ƒ      147 “      163 £    179 ³    195 Ã    211 Ó    227 ã   243 ó
   132 „      148 ”      164 ¤    180 ´    196 Ä    212 Ô    228 ä   244 ô
   133 …      149 •      165 ¥    181 µ    197 Å    213 Õ    229 å   245 õ
   134 †      150 –      166 ¦    182 ¶    198 Æ    214 Ö    230 æ   246 ö
   135 ‡      151 —      167 §    183 ·    199 Ç    215 ×    231 ç   247 ÷
   136 ˆ      152 ˜      168 ¨    184 ¸    200 È    216 Ø    232 è   248 ø
   137 ‰      153 ™      169 ©    185 ¹    201 É    217 Ù    233 é   249 ù
   138 Š      154 š      170 ª    186 º    202 Ê    218 Ú    234 ê   250 ú
   139 ‹      155 ›      171 «    187 »    203 Ë    219 Û    235 ë   251 û
   140 Œ      156 œ      172 ¬    188 ¼    204 Ì    220 Ü    236 ì   252 ü
   141       157       173 ­    189 ½    205 Í    221 Ý    237 í   253 ý
   142 Ž      158 ž      174 ®    190 ¾    206 Î    222 Þ    238 î   254 þ
   143       159 Ÿ      175 ¯    191 ¿    207 Ï    223 ß    239 ï   255



   */

   /*

     void firsttext()

     making the first line for a text-file

     automating translation into monotype-code:
     choosing all the directions in the text-file

     ^Bn = basis calculations measurement system
	 n = p,d,f
	   p=pica,      12 pica-points     = .1667 inch
	   d=didot,     12 didot-points    = .1770 inch
	   f=fournier   12 fournier-points = 11/12 didot

     ^An  = unit adding
	 n=0,1,2,3

     ^snm   adjusting the set
	 n = alphahex > 5-15
	 m = 0,1,2,3

     ^Nn  monotype coding sytem
	 n = 0 => default 15*15
	 n = 1 => NORM2   17*15
	 n = 2 => MNH     17*16
	 n = 3 => MNK     17*16
	 n = 4 => SHIFT   17*16

     ^wnm   linewidth n*10+m * 12 point

     ^Knm   adjusting the wedge
	 n = row-number - 1
	   0-f hex
	   0,1,2,3,4,  5,6,7,8,9, a,b,c,d,e,  f
	 m = unit value f the row
	   4,5, 6,7,8,9,a, b,c,d,e,f, g,h,i,j,k, l,m,n,o,p =25

     ^Ln   n = 1,2,3   = lengh ligature

   */


   /* vars in zoek() */

   int zoek_rci;
   int zoek_rcnr;
   int zoek_rcgevonden ;
   int zoek_rcsum;
   char zoek_rcc;
   unsigned char zoek_rcst;
   unsigned char zoek_rclen;

   /* vars in get_line */

   int gllimit;
   int gli;
   char glc;

   /* vars in menu */

   char mc;
   int  stored;
   int  fgelezen;

   /* vars in read_inputname */

   int sts_try,fo;

   /* vars in functions storing files */

   char mfile[7000];
   int  nmfile;
   char recstring[22] = "\"     , ,  ,  ,  ,";
   char r2str[22];
   int  matmax = 340;
   char matstring[120];
   int  lmatstr;

   /* vars in read_mat() */

   int regel_tootaal;  /* ??? */
   int tst_i;

   /* vars in leesregel() */
   int  crp_i;
   char crp_l;
   int  eol;

   /* var in alphahex() */
   unsigned char alpha_add;

   /* var in aanvullen() */
   char all[4];

   #include <c:\qc2\globals.c>

   /* var invoegen() */
   char ill[4];
   struct matrijs imat;
   int j_nv ,nr_nv ;

   /******************* function declarations ***********************/

   void  make_matrec(int nr);
   char  ce();
   int   i_abs( int a );
   void  print_at(int r, int c, char *s);
   void  cls();
   void  introm();
   void  menu();
   void  cler_matrix ();
   void  store_mat();
   int   get_line();
   int   test_EOF();
   int   alphahex ( char c );
   void  clr_buf();
   void  r_mat ( int r );
   void  r_mat2( int rij, int kol , int r );

   void  part2 ( int  r ); /* 30 march 2006 */

   int   get__row(int row, int co);
   int   get__col( int row, int col);
   unsigned char
	 get__srt(int row, int col );
   int   lig__get(int row, int col);
   char  displaym();
   void  scherm3( void);
   void  scherm2();
   void  pri_coln(int column); /* prints column name */
   void  pri_lig( struct matrijs *m );
   void  read_mat( );
   void  read_inputname();
   void  read_outputname(int s);
   void  disp_matttt(int nr);
   unsigned char
	convert ( char a, char b );
   void  leesregel();
   char  lees_txt( long nr  );
   int   get___int(int row, int col);
   void  invoegen();
   int   zoek( char l[], unsigned char s, int max );
   void  edit();
   void  new();
   char  rd_number();
   void  aanvullen();
   void  aanvullen2();
   #include <c:\qc2\function.c>


   void vulaan( int vnr ,int bron, int s );
   void wisa(int vnr);
   void ask_storage();  /* added 28-3-2006 */
   void wedge();
   void firsttext();








   void firsttext()
   {
      /* data lezen */
      /* file openen */
      /* read_outputname( 2 ); */
      /* regel maken */
      /* wegschrijven */
      /* file sluiten */

   }

   /* function added 30-3-2006 */

   void wedge()
   {
       int i, max, l;
       double f;
       char cw;

       cls();
       print_at( 5,20,"     What system ? ");
       print_at( 7,20,"       15*15 = 1");
       print_at( 8,20,"       17*15 = 2");
       print_at( 9,20,"   MNH 17*16 = 3");
       print_at(10,20,"   MNK 17*16 = 4");
       print_at(11,20," SHIFT 17*16 = 5");
       do {
	  print_at(13,20,"                  ");
	  print_at(13,20,"      system =");
	  cw = getchar();
       }
	  while ( cw < '1' || cw > '5' );
       cw--;
       central.syst = cw - '0' ;
       switch ( cw ) {
	  case '0' : max = RIJAANTAL - 1 ; break;
	  case '1' : max = RIJAANTAL - 1 ; break;
	  case '2' : max = RIJAANTAL ; break;
	  case '3' : max = RIJAANTAL ; break;
	  case '4' : max = RIJAANTAL - 1 ; break;
	      /* wedge with SHIFT-system has 15 positions */
       }

       print_at(14,20,"Read unit values rows ");

       for (i=0; i < max; i++) {
	   print_at(16,8+ 4*i,"");
	   printf("%2d  ",i+1);
       }

       for (i=0; i < max ; i++ ) {
	    do {
	       print_at(20,20,"                    ");
	       print_at(20,20,"row ");
	       printf("%2d  units = ",i+1);

	       get_line();
	       wig[i] = atoi(line_buffer);
	    }
	       while (wig[i] < 3 );

	    print_at(17,8+4*i,"");
	    printf("%2d  ",wig[i]);
       }

       if (central.syst == SHIFT ) wig[15]=wig[14];

       cls();
       do {
	  print_at(10,29,"        ");
	  print_at(10,20,"Set   = ");
	  get_line();
	  f = atof(line_buffer);
       }
	  while ( f < 4. || f >16. );
       f += .125; f *= 4;
       central.set = (int) f;
   }

   void vulaan( int vnr, int bron, int s )
   {
       matrix[vnr].lig[0] = matrix[bron].lig[0];
       matrix[vnr].lig[1] = matrix[bron].lig[1];
       matrix[vnr].lig[2] = matrix[bron].lig[2];

       matrix[vnr].w      = matrix[bron].w;
       matrix[vnr].mrij   = matrix[bron].mrij;
       matrix[vnr].mkolom = matrix[bron].mkolom;
       matrix[vnr].srt    = s;
   }

   void wisa(int vnr)
   {
	 matrix[vnr].lig[0] = all[0];
	 matrix[vnr].lig[1] = all[1];
	 matrix[vnr].lig[2] = all[2];

	 matrix[vnr].w      = 9;
	 matrix[vnr].srt    = 6;
   }


   void aanvullen()
   {
      int i, nr;

      for (i=0;i < 3; i++ ) rd_mat.lig[i]='\0';
      rd_mat.lig[0] = ':' ; /* all[0] = ':'; */

      for (i=0;i< 3;i++) all[i]=rd_mat.lig[i];

      nr = zoek( all, 0 , matmax );

      /*
      printf(nr >= 0 ? "gevonden " : "niet gevonden ");
      printf("nr = %2d ",nr);
      ce();
       */

      nr >= 0 ? vulaan(272,nr,2 ) : wisa(272) ;

      all[0] = ';' ;
      nr = zoek( all, 0 , matmax );
      nr >= 0 ? vulaan(273,nr,2 ) : wisa(273) ;

      all[0] = '!' ;
      nr = zoek( all, 0 , matmax );
      nr >= 0 ? vulaan(274,nr,2 ) : wisa(274) ;

      all[0] = '?' ;
      nr = zoek( all, 0 , matmax );
      nr >= 0 ? vulaan(275,nr,2 ) : wisa(275) ;

      all[0] = '.' ;
      nr = zoek( all, 0 , matmax );
      nr >= 0 ? vulaan(276,nr,1 ) : wisa(276) ;
      nr >= 0 ? vulaan(277,nr,2 ) : wisa(277) ;

      all[0] = ',' ;
      nr = zoek( all, 0 , matmax );
      nr >= 0 ? vulaan(278,nr,2 ) : wisa(278) ;

      all[0] = '(' ;
      nr = zoek( all, 0 , matmax );
      nr >= 0 ? vulaan(21,nr,2 ) : wisa(291) ;

      all[0] = ')' ;
      nr = zoek( all, 0 , matmax );
      nr >= 0 ? vulaan(292,nr,2 ) : wisa(292) ;

      all[0] = '\'' ;
      nr = zoek( all, 0 , matmax );
      nr >= 0 ? vulaan(279,nr,2 ) : wisa(279) ;

      all[0] = '`' ;
      nr = zoek( all, 0 , matmax );
      nr >= 0 ? vulaan(280,nr,2 ) : wisa(280) ;

      all[0] = '\256' ;
      nr = zoek( all, 0 , matmax );
      nr >= 0 ? vulaan(287,nr,2 ) : wisa(287) ;
      nr >= 0 ? vulaan(289,nr,1 ) : wisa(289) ;

      all[0] = '\257' ;
      nr = zoek( all, 0 , matmax );
      nr >= 0 ? vulaan(290,nr,1 ) : wisa(290) ;
      nr >= 0 ? vulaan(288,nr,2 ) : wisa(288) ;

      all[0] = '-' ;
      nr = zoek( all, 0 , matmax );
      nr >= 0 ? vulaan(281,nr,1 ) : wisa(281) ;
      nr >= 0 ? vulaan(282,nr,2 ) : wisa(282) ;

      all[1] = '-' ;
      nr = zoek( all, 0 , matmax );
      nr >= 0 ? vulaan(283,nr,1 ) : wisa(283) ;
      nr >= 0 ? vulaan(284,nr,2 ) : wisa(284) ;

      all[2] = '-' ;
      nr = zoek( all, 0 , matmax );
      nr >= 0 ? vulaan(285,nr,1 ) : wisa(285) ;
      nr >= 0 ? vulaan(286,nr,2 ) : wisa(286) ;
   }





   void introm()
   {
       cls();
       printf("\n\n\n\n");

       printf("       ***************************************************************\n");
       printf("       *                                                             *\n");
       printf("       *            matrix : manipulation with diecases              *\n");
       printf("       *                                                             *\n");
       printf("       *               version 0.0.1.  28 march 2006                 *\n");
       printf("       *                                                             *\n");
       printf("       *        John Cornelisse   computer-2-caster-project          *\n");
       printf("       *                                                             *\n");
       printf("       ***************************************************************\n");
       printf("\n                                       ");

       ce();
   }

   /* 18 mrt 2006 */

   void disp_matttt(int nr)
   {
      int dmi;

      printf("Matrix  %3d ",nr);
      printf("lig = ");
      for (dmi=0; dmi<3 ; dmi++)
	 printf("%1c",matrix[nr].lig[dmi]);
      dmi = matrix[nr].lig[0];
      printf(" = %4d ", dmi );
      printf(" s = %1d ", matrix[nr].srt);
      printf(" w = %2d ", matrix[nr].w);
      printf(" r = %2d ", matrix[nr].mrij);
      printf(" c = %2d ", matrix[nr].mkolom);
      ce();
   }




   void part2( int r)
   {
       int i,w;

       for (lrj=0; lrj < nlineb; lrj++)
	  printf("%1c",line_buffer[lrj]);
       clr_buf();
       do {
	  print_at(r,16,"           ");
	  print_at(r,16," = ");
	  lign = lig__get (r, 18);
       }
	  while (lign < 0 );

       if ( lign > 0 ) {
	  print_at(r,15," = ");
	  for (i=0;i<3 && line_buffer[i] != '\0' ; i++) {
	     printf("%1c",line_buffer[i]);
	     rd_mat.lig[i]=line_buffer[i];
	  }
	  do {
	     print_at(r,22,"Width in units ");
	     print_at(r,39,"");
	     w = get___int(r, 38);
	  }
	     while (w < wig[rd_mat.mrij] -2 || w > 23 );
	  rd_mat.w = w;
	  print_at(r,22,"width           ");
	  print_at(r,28,"");
	  printf("%2d kind ",rd_mat.w);
	  rd_mat.srt = get__srt(r,36);
       }
       else {
	  rd_mat.w   = wig[ rd_mat.mrij ];
	  rd_mat.srt = 0;
       }
   }
   /* version 30-3-2006 */

   void r_mat2 ( int row, int column, int r )
   {
       int i;

       print_at(r,1,"                                                ");
       print_at(r,1,"Read mat ");
       clr_buf();
       rd_mat.mrij = row;
       rd_mat.mkolom = column;
       for (i=0;i<3;i++) rd_mat.lig[i]='\0';

       switch (column ) {
	  case  0 : line_buffer[nlineb++] ='N';
		    line_buffer[nlineb++] ='I'; break;
	  case  1 : line_buffer[nlineb++] ='N';
		    line_buffer[nlineb++] ='L'; break;
	  default :
		    line_buffer[nlineb++] ='A' + column - 2; break;
       }
       line_buffer[nlineb++] ='-';
       if ( row < 10 )  line_buffer[nlineb++] = '1' + row ;
       if ( row > 10 )  {
	   line_buffer[nlineb++] ='1';
	   line_buffer[nlineb++] = ( row % 10 ) + '0';
       }


       part2 ( r );

   }   /*  w */



   /* version 28-3-2006 */

   void r_mat ( int r )
   {
       int i;

       print_at(r,1,"                                                ");
       print_at(r,1,"Read mat ");
       clr_buf();
       rd_mat.mrij = 0;
       rd_mat.mkolom = 0;
       for (i=0;i<3;i++) rd_mat.lig[i]='\0';

       print_at(r,11,"Column ");
       rd_mat.mkolom = get__col(r,18);

       line_buffer[nlineb++] ='-';
       printf(" row                     ");
       rd_mat.mrij = get__row(r,25 );

       print_at(r,11,"                                     ");
       print_at(r,11,"");

       part2 ( r );
   }


   void invoegen()
   {
       for (j_nv=0;j_nv<3;j_nv++) ill[j_nv] = rd_mat.lig[j_nv];

       nr_nv = zoek( ill, rd_mat.srt , matmax );

       /*
       print_at(24,30," nr_nv = ");
       printf("%3d ",nr_nv);
       cls(); printf("Invoegen ");ce();
	*/

       if ( nr_nv >= 0 ) {

	   /* printf("record found %3d lig =",nr_nv );
	      for ( j_nv=0;j_nv<3;j_nv++) printf("%1c",matrix[nr_nv].lig[j_nv]);
	      printf(" r %2d k %2d s %1d ",matrix[nr_nv].mrij,
					matrix[nr_nv].mkolom,
					matrix[nr_nv].srt);
	      ce();
	   */

	   for ( j_nv=0; j_nv<3; j_nv++) matrix[nr_nv].lig[j_nv] = '\0';
	   matrix[nr_nv].srt = 0;
	   matrix[nr_nv].w = wig[ matrix[nr_nv].mrij ] ;
	   imat = matrix[nr_nv];
	   pri_lig( & imat );
       }
	    /* else {
		printf("record NOT FOUND ");
	     }
	     */

       /* change place with mat */
       nr_nv = rd_mat.mrij * 17 + rd_mat.mkolom ;
       for ( j_nv=0; j_nv<3; j_nv++)
	      matrix[nr_nv].lig[j_nv] = rd_mat.lig[j_nv];
       matrix[nr_nv].srt = rd_mat.srt;
       matrix[nr_nv].w   = rd_mat.w;
       imat              = matrix[nr_nv];
       pri_lig ( & imat );
   }

   /* version 28-3-2006 */


   void edit()
   {
       char ecc;

       displaym();
       do {
	  r_mat(24);
	  invoegen();

	  print_at (23,20,"end reading = ");
	  ecc = ce();
       }
	  while ( ecc != '=' );
   }
   /* 30 march 2006 */

   int newi,newj;

   void new()
   {
       char ecc;

       displaym();
       for ( newj = 0; newj < 15; newj++) {
	  for (newi = 0; newi < 17 ; newi++) {
	     r_mat2 ( newj, newi, 24);
	     invoegen();
	     ce();
	  }
       }

       /*
       do {
	  r_mat(24);
	  invoegen();

	  print_at (23,20,"end reading = ");
	  ecc = ce();
       }
	  while ( ecc != '=' );
	*/
   }



   void ask_storage()
   {
      cls();
      do {
	 print_at(5,5,"File is not saved ");
	 print_at(7,5,"Save file ? ");
	 mc = getchar();
	 if (mc >='A' && mc<='Z') mc = mc - 'A' + 'a' ;
	 switch (mc) {
	    case 'j' :
	    case 'y' :
	       mc = 'y';
	       store_mat();
	       stored = 1;
	       break;
	    case 'n' :
	       mc = 'n';
	       stored = 0;
	       break;
	    default :
	       mc = ' ';
	       break;
	 }
      }
	 while (mc != 'n' && mc != 'y');
   }
   /* version 28-3-2006 */



   void menu()
   {
      stored   = 1;

      do {
	 cls();
	 print_at( 4,30," Editing Diecase-files");
	 print_at( 6,30,"      new file   = n ");
	 print_at( 7,30,"      read file  = r ");
	 print_at( 8,30,"      display    = d ");
	 print_at( 9,30,"      store file = s ");
	 print_at(10,30,"      edit file  = e ");
	 print_at(11,30,"      new wedge  = w ");
	 print_at(12,30,"  first textline = f ");
	 print_at(14,30,"     < stop = '#' > ");
	 print_at(16,30,"    command = ");
	 mc = getchar();
	 switch(mc) {
	    case 'f' : /*first text line */
	       firsttext();
	       break;
	    case 'w' : /* change wedge    */
	       wedge();
	       break;
	    case 'n' : /* new diecase     */
	       if ( ! stored )
		  ask_storage();
	       cler_matrix();
	       new();        /* edit(); */
	       aanvullen();
	       stored = 0;
	       break;
	    case 'd' : /* display file    */
	       displaym();
	       ce();
	       break;
	    case 'r' : /* read file       */
	       if ( ! stored )  ask_storage();
	       read_mat();
	       displaym();
	       ce();
	       stored = 1;
	       break;
	    case 's' : /* store file      */
	       store_mat();
	       stored = 1;
	       break;
	    case 'e' : /* edit file       */
	       if ( ! stored )
		  ask_storage();
	       edit();
	       aanvullen();
	       stored = 0;
	       break;
	 }
      }
	  while ( mc != '#');

      if ( ! stored ) ask_storage();
   }

   /* version 28-3-2006 */

   main()
   {
       introm();
       menu();
   }













