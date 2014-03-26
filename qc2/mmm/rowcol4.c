  /***************************************************************
   *                                                             *
   *          matrix : manipulation with diecases                *
   *                                                             *
   *          maart 2006                                         *
   *                                                             *
   *                                                             *
   *                                                             *
   ***************************************************************/

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

  #include <c:\qc2\globals3.c>

  int matmax = 340;
  char matstring[120];
  int  lmatstr;
  /*
  struct RECORD {
       char regel[80];
  } wfilebuf ;
   */

  struct RECORD {
      char    string[80];
  } wfilerec ; /*= { 0, 1, 10000000.0, "eel sees tar" }; */

  size_t wrecsize = sizeof( wfilerec );

  char recstring[22] = "\"     , ,  ,  ,  ,";
  char r2str[22];

  void ce();

  /*
   struct RECORD {
      int     integer;
      long    doubleword;
      double  realnum;
      char    string[15];
   } filerec = { 0, 1, 10000000.0, "eel sees tar" };
   main()
   {
      int c, newrec;
      size_t recsize = sizeof( filerec );
      FILE *recstream;
      long recseek;

      /   Create and open temporary file.   /
      recstream = tmpfile();
      /   Write 10 unique records to file.   /
      for( c = 0; c < 10; c++ )
      {
	  ++filerec.integer;
	  filerec.doubleword *= 3;
	  filerec.realnum /= (c + 1);
	  strrev( filerec.string );
	  fwrite( &filerec, recsize, 1, recstream );
      }

    */

  char mfile[7000];
  int  nmfile;

  void  store_matrec();

  void  make_matrec(int nr);

  void  make_matrec(int mnr)
  {
      int i,l,w;
      char ccm;

      /*
	012345678901234567890
	"\214",0, 5, 0, 0,
	typedef struct matrijs {
	char lig[4]; unsigned char srt; unsigned int  w;
	unsigned char mrij  ; unsigned char mkolom;
	};
	*/

      for (i=0;i<19;i++) r2str[i]= recstring[i];
      l=0;
      for (i=0;i<3 && matrix[mnr].lig[i] != '\0' ; i++) l++;
      /*    012345678901234567890
	    "\214",0, 5, 0, 0, */

      switch (l ) {
	 case 0 : /* 012345678901234567890
		     ""    ,0, 5, 0, 0,    */

	    r2str[ 1] = '\"';
	    break;
	 case 1 : /* 012345678901234567890
		     "a"   ,0, 5, 0, 0,    */
	    ccm = matrix[mnr].lig[0];
	    w = ccm;
	    /*
	       printf(" c= %1c %4d ",ccm,ccm);
	       ce();
	     */
	    if ( w > 0 ) {
		r2str[ 1] = matrix[mnr].lig[0];
		r2str[ 2] = '\"';
	    } else {
		w += 256;
		r2str[ 4] = ( w % 8) + '0' ;
		w -= ( w % 8 );
		w /= 8;
		r2str[ 3] = (w % 8) + '0' ;
		w -= ( w % 8 );
		w /= 8;
		r2str[ 2] = (w % 8) + '0' ;
		r2str[ 1] = '\\';
		r2str[ 5] = '\"';
	    }
	    break;
	 case 2 : /* 012345678901234567890
		     "aa"  ,0, 5, 0, 0, */

	    r2str[ 1] = matrix[mnr].lig[0];
	    r2str[ 2] = matrix[mnr].lig[1];
	    r2str[ 3] = '\"';
	    break;
	 default :
	    r2str[ 1] = matrix[mnr].lig[0];
	    r2str[ 2] = matrix[mnr].lig[1];
	    r2str[ 3] = matrix[mnr].lig[2];
	    r2str[ 4] = '\"';
	    break;
      }
      r2str[ 7] = matrix[mnr].srt + '0';
      r2str[ 9] = ( matrix[mnr].w > 9 ) ? matrix[mnr].w / 10 + '0' : ' ';
      r2str[10] = ( matrix[mnr].w % 10) + '0';
      r2str[12] = ( matrix[mnr].mrij > 9 ) ?
		matrix[mnr].mrij / 10 + '0' : ' ';
      r2str[13] = ( matrix[mnr].mrij % 10) + '0';
      r2str[15] = ( matrix[mnr].mkolom > 9 ) ?
		matrix[mnr].mkolom / 10 + '0' : ' ';
      r2str[16] = ( matrix[mnr].mkolom% 10) + '0';

      /*
	printf("String =");
	for (i=0;i<18;i++) printf("%1c",r2str[i]);
	ce();
	*/
      r2str[19]='\0';
      r2str[20]='\0';
  }

  unsigned char mcx[5];

  void  store_matrec()
  {
      int i;

      printf("\nlmatsts = %4d string = ",lmatstr );

      for (i =0; i<lmatstr ; i++) {

	    wfilerec.string[i] = matstring[i];
	    printf("%1c",wfilerec.string[i]);
	  /*  fputc( matstring [i], foutcode );*/
      }
      /*
      typedef struct RECORD {
	 char regel[80];
      } wfilebuf ;
      */

      printf("\n");

      /*
  size_t wrecsize = sizeof( wfilerec );
       */

      fwrite(  &wfilerec , wrecsize , 1, foutcode );


      /*
   struct RECORD {
      int     integer;
      long    doubleword;
      double  realnum;
      char    string[15];
   } filerec = { 0, 1, 10000000.0, "eel sees tar" };
   main()
   {
      int c, newrec;
      size_t recsize = sizeof( filerec );
      FILE *recstream;
      long recseek;

      /   Create and open temporary file.   /
      recstream = tmpfile();
      /   Write 10 unique records to file.   /
      for( c = 0; c < 10; c++ )
      {
	  ++filerec.integer;
	  filerec.doubleword *= 3;
	  filerec.realnum /= (c + 1);
	  strrev( filerec.string );
	  fwrite( &filerec, recsize, 1, recstream );
      }
      */



      printf("\nklaar ");

      lmatstr = 0;
      printf("lmatstr = %4d ",lmatstr);

      ce();
      /*
	 fputc( mcx[1], foutcode );
	 fputc( mcx[2], foutcode );
	 fputc( mcx[3], foutcode );
	 fputc( mcx[4], foutcode );
       */
  }

  int      i_abs( int a );
  void print_at(int r, int c, char *s);
  void cls();
  void introm();
  void menu();
  void cler_matrix ();
  void store_mat();
  int get_line();
  int test_EOF();
  void a_b(int row, int col, int ibb );
  void add_buf(int row,int col, int ibb, char c);
  int  alphahex1 ( char c );
  void clr_buf();
  void r_mat ( int r );
  int  get__row(int row, int co);
  int  get__col( int row, int col);
  void displaym();
  void scherm3( void);
  void scherm2();
  void pri_coln(int column); /* prints column name */
  void pri_lig( struct matrijs *m );
  void read_mat( );
  void read_inputname();
  void read_outputname();
  void disp_matttt(int nr);
  unsigned char convert ( char a, char b );
  void leesregel();
  char lees_txt( long nr  );
  int  get___int(int row, int col);
  void invoegen();
  int zoek( char l[], unsigned char s, int max );


  void ce()
  {
     if ( getchar()=='#') exit(1);
  }

  int      i_abs( int a )
  {
     return ( a < 0 ? -a : a );
  }

  int zoek_rci;
  int zoek_rcnr;
  int zoek_rcgevonden ;
  int zoek_rcsum;
  char zoek_rcc;
  unsigned char zoek_rcst;
  unsigned char zoek_rclen;

   int zoek( char l[], unsigned char s, int max )
   {
      zoek_rcgevonden = FALSE;
      zoek_rcnr  = -1;
      zoek_rcsum =  0;
      zoek_rcst  =  s;

      /*
      printf("in zoek: l = %1c%1c%1c \n",l[0],l[1],l[2]);
      printf("srt = %1d ",s);
      if (getchar()=='#')exit(1);
       */
      if ( zoek_rcst == 2) {   /* only lower case will be small caps */
	 if (  (l[0] < 97) || (l[0] > 122) ){
	    zoek_rcst = 0;
	 }
      }

	      /* italic/small cap point as roman point */
      zoek_rclen = 0;
      for (zoek_rci=0; zoek_rci<4 && l[zoek_rci] != '\0'; zoek_rci++)
      {  /* determine length l[] */
	 if (l[zoek_rci] != '\0') zoek_rclen++;
      }
      if (zoek_rclen == 1)   /* for now: no italic or small-cap points */
      {
	 switch (l[1])
	 {
	    case '.' :
	      if (zoek_rcst != 3) zoek_rcst = 0;
	      break;
	    case '-' :
	      if (zoek_rcst != 3) zoek_rcst = 0;
	      break;
	 }
      }
      do {
	  zoek_rcnr ++;
	  zoek_rcsum = 0;
		 /* unicode => 4 */
	  for (zoek_rci=0, zoek_rcc=l[0] ;
		 zoek_rci< 3 /* && zoek_rcc != '\0'*/ ;
			      zoek_rci++) {
	     zoek_rcc = l[zoek_rci];

	     /*
	     printf("l[%1d] = %3d m.lig[] = %3d ",zoek_rci,zoek_rcc ,
			       matrix[zoek_rcnr].lig[zoek_rci]);
	      */
	     zoek_rcsum +=
		i_abs( zoek_rcc - matrix[zoek_rcnr].lig[zoek_rci] );
	       /* printf("sum = %4d \n",zoek_rcsum); */
	  }
	  /*
	  if (zoek_rcsum < 10 ) {
	      printf("Sum = %6d nr = %4d ",zoek_rcsum,zoek_rcnr);
	      printf("m %3d %3d %3d   srt = %1d ",
		      matrix[zoek_rcnr].lig[0],
		      matrix[zoek_rcnr].lig[1],
		      matrix[zoek_rcnr].lig[2],
		      matrix[zoek_rcnr].srt );
	      ce();

	  }
	  */
	  zoek_rcgevonden = ( (zoek_rcsum == 0 ) &&
		  ( matrix[zoek_rcnr].srt == zoek_rcst ) ) ;
	  /*
		printf(" gevonden %2d sum %3d s1 %2d s2 %2d r %2d k %2d lig %1c %1c",
		zoek_rcgevonden,zoek_rcsum, matrix[zoek_rcnr].srt , zoek_rcst,
		    matrix[zoek_rcnr].mrij,
		    matrix[zoek_rcnr].mkolom,
		    matrix[zoek_rcnr].lig[0],
		    l[0] );
		if (getchar()=='#') exit(1);
	  */
	  if (zoek_rcnr > matmax ) exit(1);
      }
	  while ( (zoek_rcgevonden == FALSE) && ( zoek_rcnr < max - 1 ) );
	  /* printf("Na de lus "); ce(); */
      if (zoek_rcgevonden == TRUE){
	 return ( zoek_rcnr );
      } else
	 return ( -1 );
   } /* zoek */

   void store_mat()
   {
      int i,j,sn;

      nmfile = 0;

      printf("store mat ");
	/* lees filenaam
	   open output file
	*/

      inpathtext[0]='\0';
      inpathtext[1]='\0';

      cls();
      printf("Give name matrix file \n\n");
      read_outputname();

      for (j=0;j< 80; j++) {
	     wfilerec.string[j] = '\0';
      }
      /*
  size_t wrecsize = sizeof( wfilerec );
       */

      lmatstr=0;
      for ( i =0; i< matmax ; i++) {
	 make_matrec( i );
	 for ( j=0; j<18; j++) matstring[ lmatstr ++ ] = r2str[j];
	 if ( (i +1) %4 == 0) {
	    printf("Insert ^CR \n");
	    matstring[lmatstr++] ='^';
	    matstring[lmatstr++] ='C';
	    matstring[lmatstr++] ='R';
	    matstring[lmatstr++] = 10 ;
	    matstring[lmatstr++] = 13 ;
	    matstring[lmatstr++] = '\0' ;

	    for (j=0; j< lmatstr-1 ; j++) printf("%1c",matstring[j]);
	    printf("\n");
	    for (j = 0; j < lmatstr -1 ; j++)
		mfile[nmfile++] =matstring[j];
	    /*
	    store_matrec();
	     */
	    for (j=0;j< 80; j++) matstring[j] = '\0';
	    lmatstr = 0;

	 }
      }
      if (lmatstr > 0 ) {
	 printf("Insert ^CR \n");
	 matstring[lmatstr++] ='^';
	 matstring[lmatstr++] ='C';
	 matstring[lmatstr++] ='R';
	 matstring[lmatstr++] = 10 ;
	 matstring[lmatstr++] = 13 ;
	 matstring[lmatstr++] = '\0' ;

	 for (j=0; j< lmatstr-1 ; j++) printf("%1c",matstring[j]);
	 printf("\n");

	 /*
	 ce();
	  */
	 for (j = 0; j < lmatstr -1 ; j++)
		mfile[nmfile++] =matstring[j];
	    /*
	    store_matrec();
	     */
	 for (j=0;j< 80; j++) matstring[j] = '\0';
	 lmatstr = 0;
	 /*

	 store_matrec();
	 for (j=0;j< 80; j++)
	     wfilerec.string[j] = '\0';
	 */

      }
      printf("Insert ^EF \n");
      matstring[lmatstr++] ='^';
      matstring[lmatstr++] ='E';
      matstring[lmatstr++] ='F';
      matstring[lmatstr++] = 10 ;
      matstring[lmatstr++] = 13 ;
      matstring[lmatstr++] = '\0' ;

      for (j=0; j< lmatstr-1 ; j++) printf("%1c",matstring[j]);
      printf("\n");
      /*
      ce();
       */
      for (j = 0; j < lmatstr -1 ; j++)
		mfile[nmfile++] =matstring[j];
	    /*
	    store_matrec();
	     */
      for (j=0;j< 80; j++) matstring[j] = '\0';
      lmatstr = 0;

      /*
      store_matrec();
      for (j=0;j< 80; j++)
	     wfilerec.string[j] = '\0';
      lmatstr=0;
      */

      printf("Add comments \n");
      for (i=0;i<3; i++) {
	 printf("C%1d =",i);
	 sn = get_line();
	 for (j=0; j< sn-1 ; j++) matstring[ lmatstr++ ]=line_buffer[j];
	 matstring[lmatstr++] = 10 ;
	 matstring[lmatstr++] = 13 ;
	 matstring[lmatstr++] = '\0' ;
	 for (j=0; j< lmatstr-1 ; j++) printf("%1c",matstring[j]);
	 printf("\n");
	 for (j = 0; j < lmatstr -1 ; j++)
		mfile[nmfile++] =matstring[j];
	    /*
	    store_matrec();
	     */
	 for (j=0;j< 80; j++) matstring[j] = '\0';
	 lmatstr = 0;
	 /*
	 store_matrec();
	 for (j=0;j< 80; j++)
	     wfilerec.string[j] = '\0';
	  */
      }
      for (j=0; j<nmfile ; j++) fputc( mfile[j], foutcode );


      ce();
      printf("close file ");
      fclose( foutcode );
      ce();
   }


   char lees_txt( long nr  )
   {
      fseek  ( fintext,  nr , SEEK_SET );
      return ( (char) fgetc( fintext )  );
   }

   void introm()
   {;}
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
      if (getchar() == '#') exit(1);
   }

   int gllimit;
   int gli;
   char glc;

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

   int test_EOF()
   {
       switch ( readbuffer[0] ) {
	   case '^' :
	   case '@' :
	      if ( readbuffer[1] == 'E' && readbuffer[2] == 'F'    )
		   EOF_f = 1 ;
	      break;
	   default :
	      EOF_f = 0;
	      break;
       }
       return(EOF_f);
   }

   char mc;
   int  stored;
   int  fgelezen;

   void menu()
   {
      fgelezen = 0;
      stored = 0;
      do {
	 cls();
	 print_at( 4,10,"Editing Diecase-files");
	 print_at( 6,10,"  new file   = n ");
	 print_at( 7,10,"  read file  = r ");
	 print_at( 8,10,"  display    = d ");
	 print_at( 9,10,"  store file = s ");
	 print_at(10,10,"  edit file  = e ");
	 print_at(12,10,"  < stop = '#' > ");
	 print_at(14,10,"  command = ");
	 mc = getchar();
	 switch(mc) {
	    case 'n' : /* new diecase     */
	       cler_matrix();
	       displaym();
		       /* empty diecase   */
		       /* read all places */
	       printf("read all places ");
	       getchar();
	       break;
	    case 'd' : /* display file    */
	       displaym();
	       if ( getchar()=='#') exit(1);
	       break;
	    case 'r' : /* read file       */
	       read_mat();
	       displaym();
	       break;
	    case 's' : /* store file      */

	       store_mat();
	       break;
	    case 'e' : /* edit file       */
	       displaym();
	       break;
	 }
      }
	  while ( mc != '#');
   }


   int sts_try,fo;

   void read_inputname()
   {
       char tl;
       int ti;

       sts_try =0; fo = 0;
       do {
	  do {
	     printf(" Enter file name:" );
	     tl = get_line();
	     for (ti=0;ti<tl-1; ti++)
		inpathtext[ti]= line_buffer[ti];
	  }
	     while (strlen(inpathtext) < 5);
	  if( ( fintext = fopen( inpathtext, "rb" )) == NULL )
	  {
	     printf("Open failure" );
	     sts_try ++;
	     if (  sts_try == 5 ) exit( 1 );
	  }
	  else
	     fo = 1;
       }
	  while (! fo );
   }

   void read_outputname()
   {
      char tl;
      int ti;
      sts_try =0; fo = 0;
      do {
	 do {
	    printf(" Enter file name:" );
	    tl = get_line();
	    for (ti=0;ti<tl-1; ti++)
	       inpathtext[ti]= line_buffer[ti];
	 }
	    while (strlen(   inpathtext) < 5);
	 strcpy (outpathcod, inpathtext );
	 _splitpath( outpathcod, drive, dir, fname, ext );
	 strcpy( ext, "mat");
	 _makepath ( outpathcod, drive, dir, fname, ext );
	 if( ( foutcode = fopen( outpathcod, "w+" )) == NULL )
	 {
	    printf("output failure" );
	    sts_try ++;
	    if (  sts_try == 5 ) exit( 1 );
	 }
	 else
	    fo = 1;
      }
	 while (! fo );
   }

   unsigned char convert ( char a, char b )
   {
      unsigned char s;
      s = 0;
      if ( a >= '0' && a <= '9' ) {
	  s = 10 * (a - '0');
      }
      if ( b >= '0' && b <= '9' ) {
	  s += (b - '0') ;
      }
      return ( s );
   }



   int   opscherm;
   int   eol;

   /* 18 march */
   int crp_i;
   char crp_l;

   void leesregel()
   {
      eol = 0;
      for (crp_i=0;  crp_i<HALFBUFF-3 &&
	   (crp_l = lees_txt( filewijzer )) != EOF && ! eol ;
	       crp_i++ ){

	   filewijzer ++ ;
	   if ( crp_l != '\015' && crp_l != '\012' )
	       readbuffer[nreadbuffer ++ ] = (char) crp_l;
	   crp_fread++;

	   switch ( crp_l ) {
	      case '@' :  /*detection end of line */
	      case '^' :
		 crp_l = lees_txt( filewijzer );

		 filewijzer ++ ;
		 readbuffer[nreadbuffer ++ ] = (char) crp_l;
		 crp_fread++;
		 crp_i++;
		 if (crp_l == 'C') eol++;
		 crp_l = lees_txt( filewijzer );
		 filewijzer ++ ;
		 readbuffer[nreadbuffer ++ ] = (char) crp_l;
		 crp_fread++;
		 crp_i++;

		 if (crp_l == 'F') eol++;
		 if (crp_l == 'R') eol++;
		 if (crp_l == 'L') eol++;
		 if (crp_l == 'C') eol++;
		 if (crp_l == 'J') eol++;
		 if (eol != 2 ) eol = 0;
		 break;
	      default :
		 eol = 0;
		 break;
	   }
      }
      /*
      if (eol) {
	   printf(" crp_l = %1c eol %2d ",crp_l,eol );
	   if (getchar()=='#') exit(1);
      }
      */
      /*
	readbuffer[nreadbuffer++]= (char) '\012';
	readbuffer[nreadbuffer]='\0';
	*/
   }

   void cler_matrix ()
   {
       int ri;
       for ( ri = 0; ri < 322 ; ri ++ ) {
	  matrix[ ri ].lig[0] = '\0';
	  matrix[ ri ].lig[1] = '\0';
	  matrix[ ri ].lig[2] = '\0';
	  matrix[ ri ].lig[3] = '\0';
	  matrix[ ri ].srt = 0;
	  matrix[ ri ].w = 0;
	  matrix[ ri ].mrij = 0;
	  matrix[ ri ].mkolom = 0;
       }
   }

   /*
    read_mat()

      added & tested 9 march 2006
      changed 10 march added: function convert);
      latest version 18 march 2006
   */
   int regel_tootaal;  /* ??? */
   int tst_i;

   void read_mat( )
   {
      char tc, *pc, ti, tl;
      int  ri, rj;
      int  firstline , crr ;
      char ans;
      int  recnr=0;

      for ( ri = 0; ri < 322 ; ri ++ ) {
	 matrix[ ri ].lig[0] = '\0';
	 matrix[ ri ].lig[1] = '\0';
	 matrix[ ri ].lig[2] = '\0';
	 matrix[ ri ].lig[3] = '\0';
	 matrix[ ri ].srt = 0;
	 matrix[ ri ].w = 0;
	 matrix[ ri ].mrij = 0;
	 matrix[ ri ].mkolom = 0;
      }
      firstline = 0;
      regel_tootaal = 0;
      /*
	clear_linedata();
	kind           = 0 ;
	line_data.last = 0.;
	line_data.vs   = 0 ;
	line_data.addlines = 0;
	line_data.add  = 0 ;
	line_data.nlig = 3 ;
	line_data.para = 0 ;
	line_data.c_style = 0;
	*/
	/* default current style */
	/* line_data.dom */
      cls();
      for (tst_i=0; tst_i< MAXBUFF; tst_i++)
	   readbuffer[tst_i] = '\0'; /* at the beginning this is empty */
	   nreadbuffer = 0;
	   ntestbuf = 0;
	   inpathtext[0]='\0';
	   inpathtext[1]='\0';
	   cls();
	   printf("Give name matrix file \n\n");
	   read_inputname();
	   crp_fread  = 0;
	   filewijzer = 0;
	   nreadbuffer=0;
	   EOF_f = 0;
	   do {
	      crr = 0;
	      if ( nreadbuffer > 3 ) {
		 if ( readbuffer[nreadbuffer-3] == '^' &&
		    readbuffer[nreadbuffer-2] == 'C' ) crr = 1;
		 }
		 if (crr == 0 ) leesregel();
		 test_EOF();
		 if ( EOF_f == 0 )
		 {
		 /* disp_line(); */
		    for ( rj = 0; rj < nreadbuffer; rj +=18 ) {
		    switch ( readbuffer[rj] ) {
			 case '"' :
			    if (recnr < 322 ) {
			       matrix[ recnr ].mrij   =
				  convert ( readbuffer[rj+12] , readbuffer[rj+13] );
			       matrix[ recnr ].mkolom =
				  convert ( readbuffer[rj+15] , readbuffer[rj+16] ) ;
			       matrix[ recnr ].srt    = readbuffer[rj+7]-'0';
			       matrix[ recnr ].w      =
				   convert ( readbuffer[rj+ 9] , readbuffer[rj+10] ) ;
			       switch ( readbuffer[rj+1] ) {
				   case '\\':
				      matrix[ recnr ].lig[0] =
				      ( readbuffer[rj+2] - '0' ) * 64 +
				      ( readbuffer[rj+3] - '0' ) * 8 +
				      ( readbuffer[rj+4] - '0' ) ;
				      break;
				   case '"' :
				      break;
				   default :
				      matrix[ recnr ].lig[0] = readbuffer[rj+1];
				      if (readbuffer[rj+2] != '"') {
					matrix[ recnr ].lig[1] = readbuffer[rj+2];
					if (readbuffer[rj+3] != '"') {
					   matrix[recnr].lig[2] = readbuffer[rj+3];
					}
				      }
				      break;
			       }
			       disp_matttt(recnr);
			       recnr ++;
			    }
			    ri += 18;
			    break;
			 case '^' :
			 case '@' :
			    rj = nreadbuffer;
			    break;
		    }  /* switch */
		 } /* for loop */
	      }
	      for (rj =0; rj < nreadbuffer; rj++) readbuffer[rj] =  '\0';
	      nreadbuffer = 0;
	      if ( feof ( fintext) )  EOF_f = 1;
	   }
	      while ( EOF_f == 0 );
	   fclose ( fintext);
      }

   void pri_lig( struct matrijs *m )
   {
      print_at(4 + m -> mrij ,6+(m -> mkolom)*4,"    ");
      print_at(4 + m -> mrij ,6+(m -> mkolom)*4,"");
      switch ( m -> srt ) {
	 case 0 : printf(" "); break;
	 case 1 : printf("/"); break;
	 case 2 : printf("."); break;
	 case 3 : printf(":"); break;
      }
      printf("%1c%1c%1c",
	 m -> lig[0],
	 m -> lig[1],
	 m -> lig[2] );
   }

   void pri_coln(int column) /* prints column name */
   {
       switch (column) {
	  case 0 : printf("NI");break;
	  case 1 : printf("NL");break;
	  default :
	     printf(" %1c",63+column ); /* column A = 2 asc 65=A */
	     break;
       }
   }

   /*
     scherm2 ()
       display skeleton on screen

    28-12-2003
    */
   int nrows;
   int scherm_i;

   void scherm2()
   {
       cls();
       for (scherm_i=0;scherm_i<=16;scherm_i++){
	   print_at(3,7+scherm_i*4,"");
	   pri_coln(scherm_i);
       }
       switch ( central.syst ) {
	   case NORM  : nrows = RIJAANTAL-1 ; /* 15*15 */
	       break;
	   case NORM2 : nrows = RIJAANTAL -1; /* 17*15 */
	       break;
	   case SHIFT : nrows = RIJAANTAL;    /* 17*16 with Shift */
	       break;
	   case MNH   : nrows = RIJAANTAL;    /* 17*16 with MNH */
	       break;
	   case MNK   : nrows = RIJAANTAL;    /* 17*16 with MNK" */
	       break;
       }
       if (nrows > RIJAANTAL   ) nrows = RIJAANTAL;
       if (nrows < RIJAANTAL -1) nrows = RIJAANTAL -1;
       for ( scherm_i=0; scherm_i <= nrows-1; scherm_i++){
	   print_at(scherm_i+4,1,"");  printf("%2d",scherm_i+1) ;
	   print_at(scherm_i+4,78,""); printf("%2d",wig[scherm_i]);
	   if (scherm_i > 18)  if (getchar()=='#') exit(1);
       }
   }

   void scherm3( void)
   {
       print_at(20,10,"corps: ");
       for (scherm_i=0;scherm_i<10;scherm_i++) {
	   if ( cdata.corps[scherm_i]>0 )  {
	       printf("%5.2f ", .5 * (double) cdata.corps[scherm_i] );
	   }
	   else printf("      ");
       }
       print_at(21,10,"set  : ");
       for (scherm_i=0;scherm_i<10;scherm_i++) {
	  if ( cdata.csets[scherm_i]>0 ) {
	      printf("%5.2f ", .25 * (double) cdata.csets[scherm_i] );
	  }
	  else printf("      ");
       }
   }
   /*
      displaym: display the existing matrix
      28-12-2003
	 scherm2();
	 pri_lig( & mm );
	 scherm3();
     */

   int    dis_i ;
   char   dis_c;
   struct matrijs dis_mm;

   void displaym()
   {
      char c;
      /*
	 print_at(20,20," in displaym");
	 printf("Maxm = %4d ",maxm);
	 ontsnap("displaym");
      */
      scherm2();
      print_at(1,10," ");
      for (dis_i=0; dis_i<33 && ( (dis_c=namestr[dis_i]) != '\0') ; dis_i++)
	 printf("%1c",dis_c);
      for (dis_i=0; dis_i< 272 ; dis_i++){
	 dis_mm = matrix[dis_i];
	 pri_lig( & dis_mm );
      }
      scherm3();
      do {
	 print_at(24,10," einde display: ");
	 c= getchar();
      }
	 while ( c != '#');
   } /*  displaym() */

   void print_at(int r, int c, char *s)
   {
      _settextposition(r,c);
      _outtext( s );
   }

   void cls()
   {
      _clearscreen( _GCLEARSCREEN );
   }

   int  get___int(int row, int col)
   {
       char c;
       int  u;

       print_at(row,col,"   ");
       _settextposition(row,col);
       u = 0;
       do {
	  while (!kbhit());
	  c = getch();
	  if (c==0) getch();
	  if (c<'0' || c>'9') {
	     print_at(row,col," ");
	     print_at(row,col,"");
	  }
       }
	  while (c<'0' || c>'9' && c != 13 );
       if ( c != 13 ) {
	  _settextposition(row,col);
	  printf("%1c",c);
	  line_buffer[nlineb++]=c;
	  u =  c - '0';
	  do {
	      print_at(row,col+1,"");
	      while (!kbhit());
	      c=getch();
	      if (c != 13 && c < '0' || c > '9' ) {
		  print_at(row,col+1," ");
		  print_at(row,col+1,"");
	      } else
		  printf("%1c",c);
	  }
	     while (c!= 13 && c < '0' || c > '9' );
	  switch ( c) {
	     case 13 :
		line_buffer[nlineb++]='\0';
		break;
	     default :
		u *= 10;
		u += ( c - '0') ;
		line_buffer[nlineb++]=c;
		line_buffer[nlineb]='\0';
	     break;
	  }
       }
       /*
	 printf("u = %3d ",u);
	 if (getchar()=='#') exit(1);
	*/
       return (u);
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

   char rd_number();

   char rd_number()
   {
       char c;
       do {
	  while ( ! kbhit() );
	  c = getche();
       }
	  while ( c < '0' || c > '9' && c != 13 );
       return(c);
   }

   int read_int()
   {
       char c; int w;
       w = 0;
       c = rd_number();
       if ( c != 13 ) {
	  w = c - '0';
	  c = rd_number();
	  if ( c != 13 ){
	     w *= 10 ;
	     w += (c - '0');
	  }
       }
       return(w);
   }

   unsigned char get__srt(int row, int col );

   unsigned char get__srt(int row, int col )
   {
       unsigned char c;

       print_at(row,col,"              ");
       _settextposition(row,col);
       do {
	  while (!kbhit());
	  c=getche();
	  if (c==0) getch();
	  if (c<'0' || c>'5') {
	     print_at(row,col," ");
	     print_at(row,col,"");
	  }
       }
	  while (c<'0' || c >'5' );
       return ( c - '0');
   }

   void r_mat ( int r )
   {
       int i,w;

       print_at(r,1,"Read mat ");
       clr_buf();
       rd_mat.mrij = 0;
       rd_mat.mkolom = 0;
       for (i=0;i<3;i++)
	  rd_mat.lig[i]='\0';
       print_at(r,11,"Column ");
       lc1 = get__col(r,18 );
       rd_mat.mkolom = lc1;
       line_buffer[nlineb++] ='-';
       printf(" row                     ");
       lr1 = get__row(r,25 );
       rd_mat.mrij = lr1;
       print_at(r,11,"                                     ");
       print_at(r,11,"");
       for (lrj=0; lrj < nlineb; lrj++)
	  printf("%1c",line_buffer[lrj]);
       clr_buf();
       print_at(r,15," = ");
       lign = lig__get (r, 18);
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
   /* struct matrijs rd_mat;
      typedef struct matrijs {
	 char lig[4];
	 unsigned char srt;
	 unsigned int  w;
	 unsigned char mrij  ;
	 unsigned char mkolom;
      };
   */

   void add_buf(int row,int col, int p, char c)
   {
       _settextposition(row,col+nlineb);
       printf("%1c",c);
       line_buffer[nlineb++]= c;
   }

   void a_b(int row, int col,int p)
   {
       _settextposition(row,col+nlineb-1);
       printf("%1c",line_buffer[nlineb-1]);
       line_buffer[nlineb--]='\0';
   }

   int alphahex1 ( char c )
   {
       alpha = 0;
       if ( c >= '0' && c <= '9' ) alpha = c - '0';
       if ( c >= 'a' && c <= 'f' ) alpha = c - 'a' + 10;
       return ( alpha );
   }

   int lig__get(int row, int col)
   {
       char c, c1, c2 ;
       int  nn;

       clr_buf();
       print_at(row,col,"               ");
       do {
	  _settextposition(row,col+nlineb);
	  while ( ! kbhit() );
	  c=getch();
	  if (c==0) {
	     getch();  /* ignore function keys */
	  }
	  c2 = 0 ;
	  switch ( c ) {
	     case  0  :
		c2 = - 1;
		break;
	     case  8  :  /* backspace */
		c2 = - 1;
		if ( nlineb > 0 ) {
		   nlineb --;
		   line_buffer[nlineb]= '\0';
		   _settextposition(row,col+nlineb);
		   printf(" ");
		   _settextposition(row,col+nlineb);
		}
		break;
	     case 13 :
		break;
	     case '.' : case '?' : case '[' : case ':' : case '&' :
	     case ']' : case ';' : case '(' : case ')' : case '+' :
	     case '=' : case '*' : case '/' : case '@' : case '#' :
	     case '0' : case '1' : case '2' : case '3' : case '4' :
	     case '5' : case '6' : case '7' : case '8' : case '9' :
	     case '$' : case ' ' : case '%' : case '\\' :
		/*
		add_buf( row, col, nlineb,  c);
		nlineb ++;
		 */
		break;
	     case '-' :
		if (nlineb > 0) {
		   switch (line_buffer[nlineb-1] ){
		      case 'd': /* 208 – d0 320 */
			  line_buffer[nlineb-1]=0xd0;
			  c2 =1; /* a_b( row, col, nlineb ); */
			  break;
		      case 'D': /* 209 — d1 321 */
			  line_buffer[nlineb-1]=0xd1;
			  c2 =1; /* a_b( row, col, nlineb ); */
			  break;
		      default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			   */
			  break;
		   }
		}
		break;
	     case '>' :
		if (nlineb > 0) {
		   switch (line_buffer[nlineb-1] ){
		       case '>':
			  line_buffer[nlineb-1]=0xae;
			  c2=1; /* a_b( row, col, nlineb ); */
			  break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			  */
			  break;
		   }
		}
		break;
	     case '<' :
		if (nlineb > 0) {
		   switch (line_buffer[nlineb-1] ){
		       case '<':
			  line_buffer[nlineb-1]=0xaf;
			  c2 =1; /* a_b( row, col, nlineb ); */
			  break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			  */
			  break;
		   }
		}
		break;
	     case 'E' :
		if (nlineb == 1 ) {
		   switch (line_buffer[nlineb-1] ){
		       case 'A':
			  line_buffer[nlineb-1]=0x92;
			  c2 = 1; /* a_b( row, col, nlineb ); */
			  break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			   */
			  break;
		   }
		}
		break;
	     case 'e' :
		if (nlineb == 1 ) {
		   switch (line_buffer[nlineb-1] ){
		       case 'a':
			  line_buffer[nlineb-1]=0x91;
			  c2 = 0; /* a_b( row, col, nlineb ); */
			  break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			   */
			  break;
		   }
		}
		break;
	     case 'z' :
		if (nlineb > 0) {
		   switch (line_buffer[nlineb-1] ){
		       case 's':
			  line_buffer[nlineb-1]=0xe1;
			  c2=1; /* a_b( row, col, nlineb ); */
			  break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			   */
			  break;
		   }
		}
		break;
	     case '!' :
		if (nlineb > 0) {
		   switch (line_buffer[nlineb-1] ){
		       case 'c':
			  line_buffer[nlineb-1]=0x87;
			  c2 =1; /* a_b( row, col, nlineb );*/
			  break;
		       case 'C':
			  line_buffer[nlineb-1]=0x80;
			  c2=1; /* a_b( row, col, nlineb ); */
			  break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			  */
			  break;
		   }
		}
		break;
	     case ',' :
		if (nlineb > 0) {
		   switch (line_buffer[nlineb-1] ){
		       case 'c':
			  line_buffer[nlineb-1]=0x87;
			  c2=1; /* a_b( row, col, nlineb ); */
			  break;
		       case 'C':
			  line_buffer[nlineb-1]=0x80;
			  c2 = 1; /* a_b( row, col, nlineb ); */
			  break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			  */
			  break;
		   }
		}
		break;
	     case '~' :
		if ( nlineb > 0 ) {
		   switch (line_buffer[nlineb-1] ){
		       case 'n':
			  line_buffer[nlineb-1]=0xa4;
			  c2=1; /* a_b( row, col, nlineb ); */
			  break;
		       case 'N':
			  line_buffer[nlineb-1]=0xa5;
			  c2=1; /* a_b( row, col, nlineb ); */
			  break;
		       case 'a':
			  line_buffer[nlineb-1]=0xc6;
			  c2 =1; /* a_b( row, col, nlineb ); */
			  break;
		       case 'A':
			  line_buffer[nlineb-1]=0xc7;
			  c2=1; /* a_b( row, col, nlineb ); */
			  break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			  */
			  break;
		   }
		}
		break;
	     case '"' :
		if (nlineb > 0 ) {
		   switch (line_buffer[nlineb-1] ){
		      case 'a' :
			 line_buffer[nlineb-1]=0x84;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		      case 'e' :
			 line_buffer[nlineb-1]=0x89;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		      case 'i' :
			 line_buffer[nlineb-1]=0x8b;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		      case 'o' :
			 line_buffer[nlineb-1]=0x94;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		      case 'u' :
			 line_buffer[nlineb-1]=0x81;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		      case 'A' :
			 line_buffer[nlineb-1]=0x8e;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		      case 'E' :
			 line_buffer[nlineb-1]=0xd3;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		      case 'I' :
			 line_buffer[nlineb-1]=0xd8;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		      case 'O' :
			 line_buffer[nlineb-1]=0x99;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		      case 'U' :
			 line_buffer[nlineb-1]=0x9a;
			 c2=1; /* a_b( row, col, nlineb ); */
			 break;
		     default :
			 /*
			 add_buf( row, col, nlineb,  c);
			 nlineb++;
			  */
			 break;
		   }
		}
		break ;
	     case '`' :
		if (nlineb > 0 ) {
		   switch (line_buffer[nlineb-1] ){
		       case 'a' :
			  line_buffer[nlineb-1]=0x85;
			  c2=1;
			  break;
		       case 'e' :
			  line_buffer[nlineb-1]=0x8a;
			  c2=1;
			  break;
		       case 'i' :
			  line_buffer[nlineb-1]=0x8d;
			  c2=1;
			  break;
		       case 'o' :
			  line_buffer[nlineb-1]=0x95;
			  c2=1;
			  break;
		       case 'u' :
			  line_buffer[nlineb-1]=0x97;
			  c2=1;
			  break;
		       case 'A' :
			  line_buffer[nlineb-1]=0xb7;
			  c2=1;
			  break;
		       case 'E' :
			  line_buffer[nlineb-1]=0xd4;
			  c2=1;
			  break;
		       case 'I' :
			  line_buffer[nlineb-1]=0xde;
			  c2=1;
			  break;
		       case 'O' :
			  line_buffer[nlineb-1]=0xe3;
			  c2=1;
			  break;
		       case 'U' :
			  line_buffer[nlineb-1]=0xeb;
			  c2=1;
			  break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			  */
			  break;
		   }
		}
		break ;
	     case '\'':
		if (nlineb > 0 ) {
		   switch (line_buffer[nlineb-1] ){
		       case 'y' :
			  line_buffer[nlineb-1]=0xec;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'Y' :
			  line_buffer[nlineb-1]=0xed;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'a' :
			  line_buffer[nlineb-1]=0xa0;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'e' :
			  line_buffer[nlineb-1]=0x82;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'i' :
			  line_buffer[nlineb-1]=0xa1;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'o' :
			  line_buffer[nlineb-1]=0xa2;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'u' :
			  line_buffer[nlineb-1]=0xa3;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'A' :
			  line_buffer[nlineb-1]=0xb5;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'E' :
			  line_buffer[nlineb-1]=0x90;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'I' :
			  line_buffer[nlineb-1]=0xd6;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'O' :
			  line_buffer[nlineb-1]=0xe0;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'U' :
			  line_buffer[nlineb-1]=0xe9;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			  */
			  break;
		   }
		}
		break ;
	     case '^' :
		if (nlineb > 0 ) {
		   switch (line_buffer[nlineb-1] ){
		       case 'a' :
			  line_buffer[nlineb-1]=0x83;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'e' :
			  line_buffer[nlineb-1]=0x88;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'i' :
			  line_buffer[nlineb-1]=0x8c;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'o' :
			  line_buffer[nlineb-1]=0x93;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'u' :
			  line_buffer[nlineb-1]=0x96;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'A' :
			  line_buffer[nlineb-1]=0xb6;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'E' :
			  line_buffer[nlineb-1]=0xd2;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'I' :
			  line_buffer[nlineb-1]=0xd7;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'O' :
			  line_buffer[nlineb-1]=0xe2;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       case 'U' :
			  line_buffer[nlineb-1]=0xea;
			  c2=1; /* a_b( row, col, nlineb ); */break;
		       default :
			  /*
			  add_buf( row, col, nlineb,  c);
			  nlineb++;
			  */
			  break;
		   }
		}
		break ;
	     default :
		if ( c >= 'a' && c <= 'z') {
		   /*
		   add_buf( row, col, nlineb,  c);
		   nlineb++;
		   */
		} else {
		   if ( c >= 'A' && c <= 'Z') {
		      /*
		      add_buf( row, col, nlineb,  c);
		      nlineb++;
		      */
		   } else {
		      if (c !=13) {
			 c = 13;
			 c2 = -1;
		      }
		   }
		}
		break;
	  }
	  switch (c2 ) {
	     case 1 :
		a_b( row, col, nlineb );
		break;
	     case 0 :
		add_buf( row, col, nlineb,  c);
		break;
	  }
       }
	  while (nlineb < 4 && c != 13 );
       if (nlineb == 3 ) {
	  if ( line_buffer[1] == '/' ) {
	     switch (line_buffer[0] ) {
		case '3' :
		   if (line_buffer[2]=='4') {
		      line_buffer[0] = 0xf3;
		      line_buffer[1] = 0;
		      line_buffer[2] = 0;
		      nlineb = 1;
		      _settextposition(row,col);
		      printf("%1c   ",line_buffer[0]);
		   }
		   break;
		case '1' :
		   switch (line_buffer[2] ) {
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
       for (nn = 0;nn<3 ; nn++) {
	  if (line_buffer[nn]==13) line_buffer[nn]= '\0';
       }
       return (nlineb);
   }


   int compair (struct matrijs b , struct matrijs c );

   int compair (struct matrijs b , struct matrijs c )
   {
       int q, d, i;

       d = 0;
       for (i=0;i<3 && b.lig[i] == c.lig[i] ; i++) ;
       q = strcmp ( b.lig,c. lig);
       d = b.lig[i] - c.lig[i] ;

       printf(" q = %4d d = %3d ",q,d);
       while (getchar() != '=');
       return ( d ) ;
   }

   void invoegen()
   {
       int i,j,nr,c;
       char ll[3];

       cls();
       printf("invoegen lig = ");
       for (j=0;j<3;j++) {
	  ll[j] = rd_mat.lig[j];
	  printf("%1c",ll[j]);
       }
       printf(" srt %1d  ",rd_mat.srt);
       nr = zoek( ll, rd_mat.srt , matmax );
       printf("nr = %3d \n",nr );
	       /* zoek eerst record nr met 0,0 */
	       /*
	       for (i=0; i < 340 && ( matrix[i].mrij != 0 || matrix[i].mkolom != 0 )
		     ; i++) {;
		}
	       printf("i = %3d m.mrij %2d m.mkolom %2d \n",
		  i,  matrix[i].mrij,   matrix[i].mkolom);
	       getchar();
	       */
       if ( nr >= 0 ) {
	   /* plek gevonden  : wissen plek */
	   for ( j=0; j<3; j++) matrix[nr].lig[j] = '\0';
	   matrix[nr].srt = 0;
	   printf("wissen matrix nr %3d ",nr);
	   getchar();
       }
       nr = rd_mat.mrij * 17 + rd_mat.mkolom ;
       printf("veranderen nr = %3d  rij %2d klon %2d ",nr,rd_mat.mrij, rd_mat.mkolom );
       getchar();
       for ( j=0; j<3; j++) matrix[nr].lig[j] = rd_mat.lig[j];
       matrix[nr].srt = rd_mat.srt;
       matrix[nr].w   = rd_mat.w;
       if ( getchar()=='#') exit(1);
   }

   main()
   {
       int i,j, n ;
       char cc;

       i=0;
       cls();
       menu();
       do {
	  r_mat(24);
	  print_at(2,0,"                                           ");
	  print_at(2,0,"");
	  printf(" r1 = %2d c1 = %2d n= %2d lig = ",lr1,lc1,lign);
	  for (j=0; j<lign; j++)
	     printf("%1c",line_buffer[j]);
	  print_at(4,0,"");
	  printf(" row %2d col %2d srt %1d width %2d lig =",
	      rd_mat.mrij,rd_mat.mkolom, rd_mat.srt, rd_mat.w);
	  for (j=0; j<3; j++)
	      printf(" j=%1d %1c",j, rd_mat.lig[j]);
	  printf("\n");
	  ce();
	  i++;
	  invoegen();
	  displaym();
	  do {
	     cc = getchar();
	     if ( cc =='#') exit(1);
	  }
	     while (cc != '=');
       }
	  while (i<10);
   }



