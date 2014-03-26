/* monoinc4.c

   void  zenden2( void )
      row_test(cb);
      setrow( e2, line_uitvul[1]-1 );
      showbits(e2);
      NJ_test (cb)
      NK_test(cx)
      GS2_test(cb)

   void  displaym()
      scherm2();
      pri_lig( & mm );
      scherm3();

   void  disp_schuif( )
   void  disp_vsp(char sp)


   int   zoek( char l[], unsigned char s, int max )
   void  dispmat(int max)
   float read_real ( void )
   void  wis(int r, int k, int n)
   void  fill_line(  unsigned int u )

      float adjust ( int width row, float add)
      void  calc_kg ( int n )
      void store_kg( void )
      int  iabsoluut( int )
      verdeel ( )

   int   verdeel ( void )  /*  int  qadd = number of possible 9 spaces
   int   keerom ( void )
   void  translate( unsigned char c, unsigned char com )
   char  afscheid(void)
   void  margin( float length, unsigned char strt )
      fill_line ( units_last );
      keer_om()
      translate( reverse[j] , com );

   void  tzint1()
   void  tzint2( float maxbreedte )
   unsigned char  berek( char cy, unsigned char w )
   void  move( int j , int k )
   unsigned char  alphahex( char dig )
   void  print_c_at( int rij, int kolom, char c)
   void  calc_kg ( int n )
       adjust (int add, float add )
   void  store_kg( void )
   void  ontcijf( void )
   void  clear_lined()
   void  clear_linedata()


*/

/*zenden2*/
/*
    read tempfile ....
    delete redundant code
    add code to correct the places of the wedges

	 row_test(cb);
	 setrow( e2, line_uitvul[1]-1 );
	 showbits(e2);
	 NJ_test (cb)
	 NK_test(cx)
	 GS2_test(cb)

*/

void zenden2( void )
{
    int i,j;
    char cc;

    /* values needed to cast */

    unsigned char  cb[5];
    unsigned char  cx[5];
    unsigned char  e1[5];
    unsigned char  e2[5];
    unsigned char  p1,p2,p3,p4;
    unsigned char  line_uitvul[2];
    unsigned char  t_u[2];
    unsigned char  char_uitvul[2];
    unsigned char  unit_add = 0;

    char start_regel = 0;
    int lt, ut, tut;
    int r0,r1;
    int startregel[20]; /* stores the record-nrs of the beginning of
		the last 20 lines */

    char_uitvul[0]=3;
    char_uitvul[1]=8;


    for (i = codetemp; i>=0; i--) {

	/* read two specified records from temp-file */

	recseek = (long) ((i - 1) * recsize);
	fseek( recstream, recseek, SEEK_SET );
	fread( &temprec, recsize, 1, recstream );
	for ( j=0 ; j<5 ; j++)
	   cb[j] = temprec.mcode[j];

	recseek = (long) ((i - 2) * recsize);
	fseek( recstream, recseek, SEEK_SET );
	fread( &temprec, recsize, 1, recstream );
	for (j=0; j<5 ; j++)
	   cx[j] = temprec.mcode[j];

	/* these two records may contain information about the
	   position of the adjustment wedges

	   double justification:
	      NKJ gk u2
	      NJ  g  u1
	      "beginning" of a line
	   single justification:
	      NJ  k  u2
	      NK  g  u1
	      "character or space with S-needle"

	   if the wedges are in the desired place
	   the justifacation-code can be ignored

	   if the wedges are not placed correct, extra code is added

	   */

	   /* for (i=0; buff[i] != -1 ; ) {  */
	   /*
	      for (j=0;j<=3;j++) {
		 cx[j]=buff[i+4];
		 cb[j]=buff[i++];
	      }
	    */
	p1=1; p2=0; p3=0; p4=0;
	r1 = row_test(cb);
	r0 = row_test(cx);
	/* printf("%2d/%2d ",r0,r1);*/

	if ( (NJ_test ( cb) + NK_test(cb)) == 2) {
	   /* printf("Beginning of a line found\n
	      NKJ in the first code ...\n");
	    */
	   line_uitvul[1] = r0;
	   line_uitvul[0] = r1;
	   char_uitvul[0] = line_uitvul[0];
	   char_uitvul[1] = line_uitvul[1];
	   p1=1; p2=1; /* both codes will be needed */
	} else {
	   if ( (NJ_test (cb) + NK_test(cx) ) == 2) {
	       t_u[1] = r0;
	       t_u[0] = r1;
	       tut = r0*15+r1;
	       ut = 15*char_uitvul[1] + char_uitvul[0];
	       if (tut == ut ) {
		   /*  printf("wedges in right position:\n");
		       printf("no adjustment code is sent\n");
		       printf("code is ignored \n");
		       */
		  p1=0; p2=0; i+=4;
	       } else {
		  /*  printf("wedges out of position:\n");
		      printf("adjustment code %2d/%2d must be sent.\n",
			     t_u[1],t_u[0]);
		   */
		  p1=1; p2=1; /* both to caster */
	       }
	       char_uitvul[0] = t_u[0];
	       char_uitvul[1] = t_u[1];
	   } else {
	      if ( GS2_test(cb) == 1) {
		 /*
		    a variable space found
		  */
		 lt = 15*line_uitvul[1] + line_uitvul[0];
		 ut = 15*char_uitvul[1] + char_uitvul[0];
		 if ( ut != lt ) {
		    /*
		       make extra code to adjust the wedges to the
		       right position to cast variable spaces

		       no difference between the "old" systems and unit-adding

		       NJ   u2 k    NJ   u2 k
		       NK g u1      NK g u1

		       though the function of the code is different

		       */
		    /* printf("gs2 = variable space: wedges in wrong position\n");
		       printf("      extra code is generated during casting");get_line(); */

		    e2[0]= 0x44; /* NJ; */
		    e2[1]= 0; e2[2]= 0;
		    e2[3]= 0x01; /* k */
		    e1[0]= 0x48; /* NK; */
		    e1[1]= 0x04; /* W0075 */
		    e1[2]= 0; e1[3]= 0x0;

		    setrow( e2, line_uitvul[1]-1 );
		    p3 =1;
		    showbits(e2);
		    setrow( e1, line_uitvul[0]-1);
		    showbits(e1);
		    p4 = 1;
		    char_uitvul[0] = line_uitvul[0];
		    char_uitvul[1] = line_uitvul[1];
		 } else {
		    p1=1; p2=0;

		    /*    printf("gs2 = variable space:\n");
			  printf("wedges in right position");
			  get_line();    */
		 }
	      }
	   }
	}
	if (p3==1) {  /* NJ k u2 extra justification code */
	    showbits(e2);
	       /* to -> codefile */
	    for (j=0;j<5;j++)
	       coderec.mcode[j]=e2[j];
	    fwrite( &coderec,
		     recsize, 1,
		     foutcode  );
	}
	if (p4==1) {  /* NK g u1 extra justification code */
	    showbits(e1);
		 /* to -> codefile */
	    for (j=0;j<5;j++)
		 coderec.mcode[j]=e1[j];
	    fwrite( &coderec, recsize, 1, foutcode  );
	}
	if (p1==1) {  /* code from temp-file */
	    showbits(cb);
		 /* to -> codefile */
	    for (j=0;j<5;j++)
		 coderec.mcode[j]=cb[j];
	    fwrite( &coderec, recsize, 1, foutcode  );
	}
	if (p2==1) {
	    showbits(cx);  /* code from temp-file */
		 /* to -> codefile */
	    for (j=0;j<5;j++)
		 coderec.mcode[j]=cx[j];
	    fwrite( &coderec, recsize, 1, foutcode  );

	    i --; /* this time two records are written */
	}

	/*
	  printf("lu %2d/%2d cu %2d/%2d \n",line_uitvul[0],line_uitvul[1],
		   char_uitvul[1],char_uitvul[0]);
	  get_line();
	  cc=readbuffer[0]; if (cc=='#') exit(1);
	*/
    }
} /* end zenden2 */


/*
   displaym: display the existing matrix

   28-12-2003

     scherm2();
     pri_lig( & mm );
     scherm3();
 */
void displaym()
{
    int i,j;
    double fx;
    char c;
    struct matrijs mm;

    /*
      print_at(20,20," in displaym");
      printf("Maxm = %4d ",maxm);
      ontsnap("displaym");
     */

    scherm2();

    print_at(1,10," ");
    for (i=0; i<33 && ( (c=namestr[i]) != '\0') ; i++)
	printf("%1c",c);


    for (i=0; i< 272 ; i++){
	 mm = matrix[i];
	 pri_lig( & mm );
    }

    scherm3();

    print_at(24,10," einde display: ");
    get_line();

}

void disp_schuif( )
{
   int i;
   print_at(22,1,"plaats  = ");
   print_at(16,1,"nschuif = ");
   for (i=0;i<nschuif;i++) printf("     %1d ",i );
   print_at(17,1,"ligl[ns-1]");
   for (i=0;i<nschuif;i++) printf("     %1d ",ligl[i] );
   print_at(18,1,"rb[plrb[i]");
   for (i=0;i<nschuif;i++) printf("     %1c ",readbuffer[ plrb[i] ]);
   print_at(19,1,"plrb[ns-1]");
   for (i=0;i<nschuif;i++) printf("   %3d ",plrb[i] );
   print_at(20,1,"schuif[  ]");
   for (i=0;i<nschuif;i++) printf("%6.4f ",schuif[i]);
   print_at(21,1,"pcop[]    ");
   for (i=0;i<nschuif;i++) printf("  %4d ",  pcop[i]);
   print_at(22,1,"ligk[]    ");
   for (i=0;i<nschuif;i++) printf("     %1d ",ligk[i] );
}



void disp_vsp(char sp)
{
   print_at(12,1,"                                           ");
   print_at(12,1,sp == ' ' ? "VARSP " : "FIXED ");
   printf("nsch-1 %2d ",nschuif-1);
   printf("wsum %8.5f letters %3d ncop %4d ",
		     line_data.wsum, line_data.line_nr, ncop);
   ce();

}





/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *                                                                       *
 *     float adjust   (  width[row], float add )  27 feb 2004                  *
 *                                                                       *
 *       limits to the adjusment of character:                           *
 *                                                                       *
 *      largest reduction : 1/1  2/7 = 35 * .0005" = .0185"              *
 *      neutral           : 3/8      = 0.000"                                *
 *      max addition      : 15/15 12/7 = 187 * .0005" = .0935"           *
 *                                                                       *
 *      The width of a character is not allowed to                       *
 *      exceed the witdh of the mat. standard mats: .2"*.2"              *
 *      Do not attempt to cast a character wider than .156" 312 *.0005"  *
 *      12 point character may a little bit wider.                       *
 *                                                                       *
 *      This gives an upper limit to the width a character can be cast   *
 *                                                                       *
 *      returns: the cast width                                          *
 *                                                                       *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

float adjust  (  unsigned char width, /* units width row  */
		 float    add         /* addition to char */
		  )
{
   float  t,  tw;
   int    it, itw, itot;
   char    cx;

   t  = add * ( (float) central.set) / 5184.;
   tw = ( ( float ) ( width * central.set) ) / 5184.;

   it   = (int) ( t  * 2000. + .5 ) ;
   itw  = (int) ( tw * 2000. + .5 ) ;

   itot = itw + it;
   if ( central.set >= 48 )
   {
       if ( itot  > 332 )   /* maximizing the addition */
	  it = 332 - itw;   /* according to table
		    justification wedge positions for adding
		    complete units
		 */
   } else {
       if ( itot > 312 )
	  it = 312 - itw;
   }
   it += 53;               /* 3/8 is neutral */
   if (it <  16) it = 16;
	  /* minimum  1/1  = 3/8 -  2/7 = -.0185" */
   if (it > 240) it = 240;
	  /* minimum 15/15 = 3/8 + 12/7 = +.0935" */
   if ( ( it % 15) == 0){
       uitvul[1] = 15;
       uitvul[0] = (it / 15) -1;
   } else {
       uitvul[1] = it % 15;
       uitvul[0] = it / 15;
   }

   return ( tw + ( ( float) it) / 2000. );
}



/*
      seeks the place of a ligature in the matcase

      liniair search routine, no tables...
      keeping it simple

      24-1-2004: was unsigned char => int
      the mat-case can contain 17*16 mats, and
      the font a lot more 272

*/

int zoek( char l[], unsigned char s, int max )
{
   int i,j;
   int nr=-1;
   int gevonden = FALSE;
   int sum = 0;
   char c ;
   unsigned char st, len ;

   st = s;
   if ( st == 2) {   /* only lower case will be small caps */
      if (  (l[0] < 97) || (l[0] > 122) ){
	  st = 0;
      }
   }

	       /* italic/small cap point as roman point */
   len = 0;
   for (i=0; i<4 && l[i] != '\0'; i++)
   {  /* determine length l[] */
       if (l[i] != '\0') len++;
   }
   if (len == 1)   /* for now: no italic or small-cap points */
   {
      switch (l[1])
      {
	 case '.' :
	   if (st != 3) st = 0; break;
	 case '-' :
	   if (st != 3) st = 0; break;
      }
   }

   do {
      nr ++;
      sum =0;
		 /* unicode => 4 */
      for (i=0, c=l[0] ; i< 3 && c != '\0' ;i++) {
	   sum += abs( l[i] - matrix[nr].lig[i] );
      }

	/*
	   if (sum < 2 ) {
	      printf("Sum = %6d nr = %4d ",sum,nr);
	      ce();
	   }
	 */

      gevonden = ( (sum == 0 ) && (matrix[nr].srt == st )) ;


      if (nr > 450) exit(1);
   } while ( (gevonden == FALSE) && ( nr < max - 1 ) );

   if (gevonden == TRUE){
      return ( nr );
   } else
      return ( -1 );
}   /* max */


void dispmat(int max)
{
   int i,j;
   char c;

   for (i=0;i<max;i++){
      printf(" lig      = ");
      for (j=0;j<3;j++)     /* unicode => 4 */
	  printf("%c",matrix[i].lig[j]);
      printf(" soort    = %3d ",matrix[i].srt);
      printf(" breedte  = %3d ",matrix[i].w);
      printf(" rij      = %3d ",matrix[i].mrij);
      printf(" kolom    = %3d ",matrix[i].mkolom);

      c = getchar();
      if (c=='#') i = max;
   }
}


float read_real ( void )
{
    get_line ();
    return (atof(readbuffer));
}

void wis(int r, int k, int n)
{
     int i,n2;
     char p[80];

     n2 = n;
     if (n2 > 79) n2 = 79;
     for (i=0;i<=n2;i++)
	 p[i]=' ';
     p[i]='\0';
     print_at( 9,10,p);
}


/*
     fill_line ( unsigned int u )

     version 2 feb 2004

     version 3 feb:
	built in the possibility of variable spaces and flat filled lines

     version 4 feb:
	verdeel$, combination fixed & variable spaces

    output in: verdeelstring[]

	V = GS5,   $[1]   / $[0] = position wedges
	v = GS1    $[n+1] / $[n] = position wedges
	f = G5
	# = O15

    uses functions:

	adjust ( int , float  );
	void  calc_kg ( int n )
    28 feb:   float adjust  ( int, float );
	void store_kg( void )
	int  iabsoluut( int )
	verdeel ( )

    returns the witdh added to the line

*/

void fill_line(  unsigned int u )
{

     int i=0, n ;
     unsigned char casus;
     char cx;
     unsigned int spf;
     unsigned int spv;

     float added;

      /*
      qadd = number of 9 unit spaces, that could fill the line
      var  = number of variable spaces used to fill out the line
       */

     added = ( (float) (u * central.set) ) / 5184.;

     spv = line_data.nspaces;
     spf = line_data.nfix;

     for ( i = 2 ; i<100 ;i++ ) verdeelstring[i]=0;
     idelta = u ;


     casus = 0;
     if (idelta >=3 ) casus ++;
     if (idelta >=8 ) casus ++;
     if (idelta >=17) casus ++;
     if (idelta >=24) casus ++;


     switch (casus)
     {
	case 0 :
	   if (spv == 0 ) /* no variable spaces */
	   {
	      if ( spf > 0 ) {  /* fixed spaces */
		 verdeelstring[n++] = ( datafix.u2 > 9 ) ?
			 datafix.u2 + 'a'-10 : datafix.u2 +'0';
		 verdeelstring[n++] = ( datafix.u1 > 9 ) ?
			 datafix.u1 +'a' -10 : datafix.u1 +'0';
	      } else {          /* neither kind of spacing */
		 verdeelstring[0]='8'; /* nothing */
		 verdeelstring[1]='3';
	      }
	   } else {       /* variable spaces  */
	      if ( idelta < 0 ) {
		 if ( spv * 2 < iabsoluut(idelta) ) {
		    printf("line too wide in: fill_line() \n");
		    printf(" idelta = %4d var spaces = %3d ",idelta,spv);
		    getchar();
		    exit(1);
		    /* the adjustment wedges cannot cope with this */
		    /* minimum correction = 1/1 = -.0185" */
		 } else { /*  2 svp > iabs( idelta )
		       the adjustment wedges can still cope with this
		       situation, result a flat line...
			   */
		    calc_kg ( spv );
		    store_kg( );
		 }
	      } else {
		 calc_kg ( spv );
		 store_kg( );
	      }
	   }

	   /*
	     printf(" uitvulling %2d / %2d ",uitvul[0],uitvul[1]);
	     printf(" verdeel$ %1c %1c ",verdeelstring[0],verdeelstring[1] );
	     if ('#'==getchar()) exit(1);
	    */
	   break;
	case 1 :  /* >=4 <= 8  idelta == positive */
	   if ( spv < 3 ) {
	      var = 1;
	      adjust    ( wig[0], (float) (idelta-5)/(float) (1+spv) );
	      store_kg( );
	      verdeelstring[2] = 'v' ; /* GS1 */
	   } else {
	      calc_kg ( spv );
	      store_kg( );
	   }
	   break;
	case 2 :  /* > 8 <= 17 */
	   if ( spv < 3 ) {
	      radd = idelta - 9 ;
	      var = 1;
	      adjust( wig[4], ( (float) radd) / ( (float) (var+spv) ) );
	      store_kg( );
	      verdeelstring[2] = 'V' ; /* GS5 */
	   } else { /* flat filled line */
	      calc_kg ( spv );
	      store_kg( );
	   }
	   break;
	case 3 :  /* > 17 < 24 */
	   if ( spv < 3 ) {
	      radd = idelta - 18 ;
	      var = 2;
	      adjust ( wig[4], ((float) radd)/ ((float)(var+spv) ) );
	      store_kg( );
	      verdeelstring[2] = 'V' ; /* GS5 */
	      verdeelstring[3] = 'V' ;
	   } else {  /* flat filled line */
	      calc_kg ( spv );
	      store_kg( );
	   }
	   break;
	case 4 :  /* >= 24 */
	   var = 3;
	   qadd = idelta / 9;
	   radd =  ( idelta >=  27  ) ? idelta % 9 : idelta - 27 ;
	   adjust ( wig[4], ((float) radd)/((float) (var+spv) ) );
	   store_kg( );
	   n = verdeel( );
	   if ( (spf > 0) && (spv == 0) ) {
		 verdeelstring[n++] = ( datafix.u2 > 9 ) ?
			 datafix.u2 + 'a'-10 : datafix.u2 +'0';
		 verdeelstring[n++] = ( datafix.u1 > 9 ) ?
			 datafix.u1 +'a' -10 : datafix.u1 +'0';
	   }
	   break;
     }
}    /* fill_line  spf */


/*
    verdeel (divide)

    divides the room left at the end of a line

    output in verdeelstring[]

    alternating squares with 9 spaces, as much as possible

 */
int  verdeel ( void )  /*  int  qadd = number of possible 9 spaces
			   unsigned char var = number variable spaces
		   */
{

    unsigned int s1,s2,s3,i, n=2;

    for ( i = n ; i<100 ;i++ ) verdeelstring[i]=0;

    left = ( qadd > var ) ? ( qadd - var ) : 0 ;

    s1=0;  s2=0; s3=0;

    while ((left > 0 ) || (var > 0 ) ) {
	if (left >= 2 ) {  /* a square */
	   s1++;
	   left -=2;  /* 18 = 2 * 9 */
	   verdeelstring[n++]='#';
	}
	if (var > 0) { /* a variable space */
	     s2++;   var --;
	     verdeelstring[n++]='V';
	} else {
	    if (left > 0 ) { /*  fixed space */
		s3++;  left --;
		verdeelstring[n++]='F';
	    }
	}
    }
    return ( n );
}

/*
  keerom () : reverse verdeelstring[] => reverse[]

  in this order the code will be saved
*/
int keerom ( void )
{
   int i,n=0;

   for (i=0;i<VERDEEL;i++)
      if (verdeelstring[i] != 0 ) n = i+1;
   for (i=0;i<n; i++)
      reverse[i]= verdeelstring[n-i-1];
   reverse[n]='\0';

   return ( n );
}

/*
   translate  reverse[] to monotype code
 */

void translate( unsigned char c, unsigned char com )
{
   int i, vt;
   char cx;

   /* unsigned char revcode[4]; = global */

   for (i=0;i<4;i++) revcode[i] = 0;
   /*
   printf(" c = %1c  com = %1c ",c,com);
      if ('#'==getchar()) exit(1);
    */

   switch ( c ) {
      case '#' : /* 015 = 0,0,0,0, */
	 break;
      case 'v' :
	 revcode[1] = 0xa0; /* GS  */
	 revcode[2] = 0x40; /*   1 */
	 break;
      case 'F' : /* fixed 9 unit space */
	 revcode[1] = 0x80; /* G   */
	 revcode[2] = 0x04; /*  5  */
	 break;
      case 'V' :
	 revcode[1] = 0xa0; /* GS  */
	 revcode[2] = 0x04; /*   5 */
	 break;
      default :
	 vt = 0;
	 if ( c > '0' && c <= '9' ) {
	    vt = c - '0';
	 }
	 if ( c >= 'a' && c <='f' ) {
	    vt = c - 'a' + 10;
	 }
	 /* printf(" vt = %2d \n",vt); */
	 if (vt > 0 ) {
	    switch ( com ) {
	       case '1':
		  revcode[0] = 0x48; /* NK  */
		  revcode[1] = 0x04; /*   g */
		  break;
	       case '2':
		  revcode[0] = 0x44; /* N J  */
		  revcode[3] = 0x01; /*    k */
		  break;
	       case 'a':
		  revcode[0] = 0x48; /* NK   */
		  revcode[1] = 0x04; /*   g  */
		  break;
	       case 'b':
		  revcode[0] = 0x4c; /* NKJ   */
		  revcode[1] = 0x04; /*    g  */
		  revcode[3] = 0x01; /*     k */
		  break;
	    }
	    revcode[2] |= rijcode[vt-1][2];
	    revcode[3] |= rijcode[vt-1][3];
	 }
	 break;
   }
       /*
       for (i=0;i<4;i++) printf("%3x",revcode[i]);
       if ('#'==getchar()) exit(1);
       */
       /* cx */

} /* translate */




char afscheid(void)
{
   char c;

   do {
      printf("\n\n\n\n        another text < y/n > ? ");
      c = getchar();
   }
     while ( c != 'n' && c != 'y' && c != 'j');
   return ( c );
}


/*
      void margin  ( float length, unsigned char strt )

      lnum = number of codes stored already
      strt = 0: beginning line
      strt = 1: end of the line

   version 29-02-2004
   version  3-03-2004
      added: possibility of empty lines

      fill_line ( units_last );
      keer_om()
      translate( reverse[j] , com );

 */

void  margin(  float length, unsigned char strt )
{
    int i, j, k, nr;
    unsigned char startline;
    float maxsub;
    int   subu, units, totunit;
    char com;

    /*
    printf(" var spaces         = %3d \n",line_data.nspaces);
    printf(" regel aanvullen vs = %3d \n",line_data.vs );
    printf(" laatste regel was  = %10.4f\n",line_data.last);
    printf(" line_data.wsum     = %10.4f\n",line_data.wsum);
    printf(" regel              = %10.4f\n",central.inchwidth);
    printf(" length             = %10.4f\n",length);
    printf(" set                = %3d \n",central.set);
     */

    units = (int) (.5 + ( length * 5184. / (float) central.set ) );
    totunit = (int) (.5 + (line_data.wsum * 5184. / (float) central.set ) );

    /*
    printf(" units              = %3d\n",units);
    printf(" totunit            = %3d\n",totunit);
     */

    startline = strt;

    /* line_data.wsum += length ; */

    if (central.set < 49 ) {
       maxsub = (float) (line_data.nspaces * 2 * central.set);
    }  else {
       maxsub = (float) (line_data.nspaces * central.set);
    }
    maxsub /= 5184.;
    subu = (int) (.5 + ( maxsub * 5184. / (float) central.set ) );

    /*
    printf(" subu %4d \n",subu);
    printf("wsum   = %10.6f \n",line_data.wsum);
    printf("maxsub = %10.6f \n",maxsub);
    printf("delta  = %10.6f \n",line_data.wsum - maxsub);
    printf("linewdt= %10.6f \n",central.inchwidth);
    printf("line u = %4d    \n",central.lwidth);
    printf("tu - u = %4d    \n",totunit-units );
    ce();
    */

    if ( line_data.wsum - maxsub > central.inchwidth ) {
       p_error("line too width in function margin ");
    }

    fill_line ( units );

    /*
    for (i=0;i<100; i++) {
	 if (verdeelstring[i] != 0 )
		printf("%1c",verdeelstring[i]);
    }
    */
    nr = keerom();

    for (j=0; j< nr; j++)
    {
       /* printf(" j = %3d rev[%2d]= %1c  \n",j,j,reverse[j] ); */

       com = '0';
       if ( startline == 0 ) {
	  if (  ( reverse[j] >  '0' && reverse[i] <= '9') ||
	     ( reverse[j] >= 'a' && reverse[i] <= 'f') ) {
	     if ( ( nr - j ) <= 2 ) {
		com = (j == (nr-1) )  ? '2' : '1';
	     } else {
		com = (j == 0) ? '1': '2';
	     }
	     /*   printf("==> com = %1c ",com); getchar(); */
	  }
       } else { /* startline == 1 */
	  if (  ( reverse[j] >  '0' && reverse[i] <= '9') ||
	     ( reverse[j] >= 'a' && reverse[i] <= 'f') ) {

	     if ( ( nr - j ) <= 2 ) {
		com = (j == (nr-1) )  ? 'b' : 'a';
	     } else {
		com = (j == 0 ) ? 'a': 'b';
	     }

	     /* print_at(23,1,"");  printf("==> com = %1c ",com); */
	     /* if ( '#' == getchar() ) exit(1); */
	  }
       }
       translate( reverse[j] , com );

       switch (reverse[j]) {
	    case '#' :
	      line_data.linebuf1[lnum   ] = '#' ;
	      line_data.linebuf2[lnum ++] = ' ' ;
	      break;
	    case 'F' :
	      line_data.linebuf1[lnum   ] = ' ' ;
	      line_data.linebuf2[lnum ++] = ' ' ;
	      break;
	    case 'v' :
	      line_data.linebuf1[lnum   ] = ' ' ;
	      line_data.linebuf2[lnum ++] = ' ' ;
	      break;
	    case 'V' :
	      line_data.linebuf1[lnum   ] = ' ' ;
	      line_data.linebuf2[lnum ++] = ' ' ;
	      break;
       }
       for (k=0;k<4;k++) {
	     cop[ncop++] = revcode[k];
	     /* printf(" %3x ",revcode[k]); */
       }
       /* getchar(); */
       /* if ('#'== getchar()) exit(1); */
    }


    if (line_data.vs == 1) {
	   line_data.last = 0.;
    }

    if (line_data.vs > 0 && strt == 0 ) line_data.vs --;

    line_data.line_nr = lnum;

    /*
    print_at(23,1,"verlaten margin:");
    printf(" line_data .vs = %3d .last = %10.5f .wsum %10.5f ",
		 line_data.vs, line_data.last, line_data.wsum );
    if ('#'==getchar()) exit(1);
    */
    /* cx = getchar(); if (cx == '#') exit(1); */
}   /* margin   startline */



void tzint1()
{
    cls();
    printf(" tzint1 : gegevens ");
    printf(" set         %4d \n",  central.set);
    printf(" matrijzen   %4d \n",  central.matrices);
    printf(" syst        %4d \n",  central.syst);
    printf(" adding      %4d \n",  central.adding);
    printf(" pica_cic       %1c\n",central.pica_cicero);
    printf(" line width  %4d \n",  central.lwidth);
    ce();
}


void tzint2( float maxbreedte )
{
   char cx;

   print_at(23,1,"tzint2: marge: ");
   printf("%7.5f ncop %3d ", line_data.wsum, ncop );
   printf("maxbreedte = %7.5f line = %7.5f c = %1c ",
	  maxbreedte, central.inchwidth, readbuffer[0] );

   print_at(24,1,"");
   printf( line_data.wsum < maxbreedte ? "kleiner" : "groter");
   if ('#'==getchar()) exit(1);
   /* cx */
}

unsigned char  berek( char cy, unsigned char w )
{
   unsigned char add_squares;

   add_squares = alphahex( cy );

   while ( (line_data.wsum + add_squares * w ) > central.lwidth)
	       add_squares --;

   return( add_squares );
}

void move( int j , int k )
{
   int i;
   float ft;

   ft = line_data.wsum;

   if ( nschuif < 10 ) {           /* store */
       ligl  [ nschuif  ] = k;
       pcop  [ nschuif  ] = ncop;
       plrb  [ nschuif  ] = j;
       schuif[ nschuif++] = ft;
   }
   else {
       for (i=0; i<9 ; i++) {      /* only last 10... move */
	  ligl  [i] = ligl  [i+1] ;
	  pcop  [i] = pcop  [i+1] ;
	  plrb  [i] = plrb  [i+1] ;
	  schuif[i] = schuif[i+1] ;
       }
       ligl  [ nschuif -1 ] = k;
       pcop  [ nschuif -1 ] = ncop;
       plrb  [ nschuif -1 ] = j;
       schuif[ nschuif -1 ] = ft;
   }
}

unsigned char  alphahex( char dig )
{
   unsigned char add;

   if ( dig >= 'A' && dig <='F' )
	dig +=  ('a'-'A');
   if ( (( dig > '0') && ( dig <= '9')) ||
	(( dig >='a') && ( dig <= 'f'))  )
   {
	add = ( dig <= '9' ) ?  dig - '0' :  dig - 'a' + 10;
   }
   else  add = 0;

   return( add );
}


void print_c_at( int rij, int kolom, char c)
{
    _settextposition( rij , kolom );
    printf("%1c",c);
}

void calc_kg ( int n )
{
   adjust ( central.set < 48 ? wig[1] : wig[0] ,
	    ((float) idelta) /((float) n)
	   );
}

void store_kg( void )
{
   verdeelstring[0] = (uitvul[1] <=9 ) ?
      ('0' + uitvul[1]) : ('a' - 10 + uitvul[1]);
   verdeelstring[1] = (uitvul[0] <=9 ) ?
      ('0' + uitvul[0]) : ('a' - 10 + uitvul[0]);
}


/*
   ontcijf = decipher first two byte of "verdeelstring"
*/
void  ontcijf( void )
{
   o[0] = ( verdeelstring[1] > '9') ?
	(verdeelstring[1] - 'a' + 10) : verdeelstring[1] - '0';
   o[1] = ( verdeelstring[0] > '9') ?
	(verdeelstring[0] - 'a' + 10) : verdeelstring[0] - '0';
}


void clear_lined()
{
    /*
       initialize linedata: at the beginning of a line
     */
    int i;

    line_data.wsum = 0;
    line_data.nspaces = 0;
    line_data.nfix = 0;
    line_data.curpos = 0;
    line_data.line_nr = 0;
    line_data.linebuf1[0]='\015';
    line_data.linebuf2[0]='\015';
    line_data.linebuf1[1]='\012';
    line_data.linebuf2[1]='\012';
    for (i=2; i<200; i++) {
       line_data.linebuf1[i]='\0'; line_data.linebuf2[i]='\0';
    }
    for (i=0; i< 15; i++) {
	 ligl[i] = 0;
	 pcop[i] = 0; /* pointers naar cop */
	 plrb[i] = 0;
	 ligl[i] = 0;
    }
    npcop = 0;
    nplrb = 0;
    /* schuif reinigen */
    for (i=0;i<10;i++) schuif[i]=0;
    nschuif = 0;
}


void clear_linedata()
{
    /*
       initialize linedata: before all disecting...
     */

    line_data.last   = 0.;
    line_data.former = 0.;
    line_data.vs     = 0.;
    clear_lined();
}



