/* monoincl9

   void translate( unsigned char c, unsigned char com )
   void  margin(  float length, unsigned char strt )
      fill_line ( units_last );
      keer_om()
      translate( reverse[j] , com );
   void fill_line(  unsigned int u )
      void  calc_kg ( int n )
      float adjust  ( int, float );
      void store_kg( void )
      int  iabsoluut( int )
      verdeel ( )
   int lus ()
      alphahex( char )
      berek( )
      move(   , 1)
      line_data.wsum += gen_system ( lus_du,    / * column * /
					lus_cu, / * row  * /
					lus_bu  / * width char * /
				       );
      dispcode( letter );
      ce();
      disp_schuif(  );
      calc_maxbreedte ( );



      commands in the input text-files:

      ^01 = roman, ^01 = italic ^02 = small caps ^03 = bold

      ^ln = length ligatures line_data.nlig n = 1, 2, 3
      ^mx = next n lines start at lenght of this line
		    line_data.vs
      ^pS = start paragraph
      ^pE = End Paragraph
      ^rx = repeat signal for kerning (x=alphahex) after: | & /

      ^CR = Carriage Return: end line here
      ^CL = place text in Center Line
      ^EF = end of file

      ^Fx = '_' fixed spaces = 3 + x * .25  points
			      x = alpha-hexadicimaal  0123456789abcdef
      ^Lx = x empty lines  x = decimaal
      ^Rx = repeat signal right margin
	       x = alphahex( )
      ^Wx = width right margin
	    x = number of pica's/cicero's/fournier's (x=alphahex)
      ^|n = add next char 1-9 units
      ^/n = substract next char(s) 1/4 - 8/4 units

      ^#x = add x * 18 units, if possible
      ^=x = add x * 9 units, if possible


      ^8x   insert ascII-code on its place
      ^9x
      ^ax
      ^bx
      ^cx
      ^dx
      ^ex
      ^fx

*/



/* variables margin */

int      mar_i, mar_j, mar_k, mar_nr;
float    mar_maxsub;
int      mar_subu, mar_units, mar_totunit;
char     mar_com;

/* variables fill_line     wsum */

int fill_i=0,  fill_n ;
unsigned char fill_casus;

/* variables translate */

int trns_i, trns_vt;

int end_line;





int  lus ( char ctest )
{
   lus_geb = t3j;

   switch ( ctest )
   {
      case '\00' :  /* ignore all control characters */
      case '\01':
      case '\02':
      case '\03':
      case '\04':
      case '\05':
      case '\06':
      case '\07':
      case '\010':
      case '\011':
      case '\012':  /* linefeed = ignored */
      case '\013':
      case '\014':
		    /* \015 = 13 decimal = CR */
      case '\016':
      case '\017':
      case '\020':
      case '\021':
      case '\022':
      case '\023':
      case '\024':
      case '\025':
      case '\026':
      case '\027':
      case '\030':
      case '\032':
      case '\033':
      case '\034':
      case '\035':
      case '\036':
      case '\037':
	 t3j ++;
	 break;
      case  '^' :  /* all commands  */
	 luscy = readbuffer[t3j+1];
	 luscx = readbuffer[t3j+2];

	 print_at(12,1,"ctest =^ ");
	 printf(" t3j = %3d luscy = %1c luscx = %1c ",t3j,luscy,luscx);
	 if ('#'==getchar()) exit(1);

	 switch ( luscy )   /* readbuffer[t3j+1] */
	 {
	    case 'p' :  /* paragraph */
	       switch (luscx) {
		  case 'S' :   /* on */
		    line_data.para = 1;
		    break;
		  case 'E' :   /* off */
		    line_data.para = 0;
		    /* end of the paragraph: fill the line */
		    margin ( (central.inchwidth - line_data.wsum) , 1 );
		    break;
	       }
	       break;
	    case '0' :  /*  ^00 = roman
			    ^01 = italic
			    ^02 = lower case to small caps
			    ^03 -> bold
			 */
	       lusikind = luscx - '0';
	       if (lusikind > 3 ) lusikind = 0;
	       if (lusikind < 0 ) lusikind = 0;
	       line_data.kind = (unsigned char) lusikind;
	       break;
	    case 'L' :
	       if (luscx >='0' && luscx<='9') {
		   line_data.vs   = luscx - '0';
		   line_data.last = central.inchwidth;
	       }
	       break;
	    case 'R' : /* repeat-signal right margin */
	       lus_lw = alphahex( luscx );
	       if (lus_lw >= 0 ) {
		   line_data.rs   += lus_lw ;
	       }
	       break;
	    case 'W' : /* calculate width right margin
			     in inches
			  luscx = 0-15 pica/cicero
			  */

	       lus_rlw = (float) ( alphahex( luscx ) );
	       switch (central.pica_cicero ) {
		  case 'p' : lus_rlw *= .1776;  /* .0148 */
		    break;
		  case 'd' : lus_rlw *= .16284; /* .01357 */
		    break;
		  case 'f' : lus_rlw *= .16668; /* .01389 */
		    break;
	       }
	       line_data.right = lus_rlw ;
	       break;
	    case 'm' :  /* ^mn -> next n lines start at lenght
				     this line
			      unsigned char vs;
			      0: no white
			     >0: add last white beginning line
			    */
	       lus_lw = alphahex( luscx );
	       if (lus_lw > 0) {
		  line_data.last = line_data.wsum ;
		  line_data.vs   = lus_lw;
	       }
	       break;
	    case '|' :  /* ^|1 -> add next char 1-9 units
			    */
	       lusaddw = 0.;
	       if (luscx > '0' && luscx <= '9') {
		   lusaddw =  (float) (luscx - '0');
		   line_data.letteradd += lusaddw;
		   if (central.set > 48 ) {
		      while (line_data.letteradd < -1. )
			 line_data.letteradd += .25;
		   } else {
		      while (line_data.letteradd < -2. )
			 line_data.letteradd += .25;
		   }
		   line_data.add = 1;
	       }
	       break;
	    case '/' :  /* ^/1 -> subtract 1-8 1/4 units
			    */
	       lusaddw = 0.;
	       if ( luscx >'0' && luscx <'9') {
		   lusaddw =  (float) (luscx - '0');
		   line_data.letteradd -= lusaddw * .25;
		   line_data.add = 1;
	       }
	       lusaddw *= - .25;
	       break;
	    case 'r' : /* repeat signal for "kerning" */
	       if (fabsoluut(lusaddw) > .1) {
		   line_data.add = alphahex( luscx );
	       }
	       break;
	    case '#' :  /* ^#n add n times 18 units squares alpha-hex .... */

	       if ( ( line_data.wsum +
		    ( (float) (alphahex(luscx) * 18 * central.set) ) / 5184.)
		      > central.inchwidth ) {

		  margin(central.inchwidth - line_data.wsum, 1 );
		  /* line_data.wsum = central.inchwidth; */
	       } else {

		  lusaddsqrs = berek( luscx, 18 );
		  if (lusaddsqrs != 0 ) {
		     move( t3j,0 );
		     for ( lus_i = 0; lus_i < lusaddsqrs
			/*
			   function berek controls overflow
			   en de maxbreedte mag niet overschreden
			   worden...
			   !!!!!!!!!!!!!

			*/
			   ; lus_i++ ){

			cop[ncop++] = 0;  /* O15 */
			cop[ncop++] = 0;
			cop[ncop++] = 0;
			cop[ncop++] = 0;
			line_data.linebuf1[lnum]   = '#';
			line_data.linebuf2[lnum++] = ' ';
			line_data.line_nr ++;
			line_data.wsum +=
			    ( (float) (18 * central.set) )/5184.;
		     }
		  }
	       }
	       /* O-15 = default 18 unit space */
		  /* printf("lusaddsqrs = %2d width = %8.2f",lusaddsqrs,
			       line_data.wsum );
		       ce();
		      */
	       break;
	    case '=' :  /* ^=n -> add n half squares alphahex... */

	       if ( ( line_data.wsum +
		      ((float) ( alphahex(luscx) * 9 * central.set ) ) / 5184.)
		      > central.inchwidth ) {

		  margin(central.inchwidth - line_data.wsum, 1 );

		  /* line_data.wsum = central.inchwidth; */
	       } else {

		  lusaddsqrs = berek( luscx, 9 );
		  if (lusaddsqrs != 0 ){
		     move(t3j,0);
		     for ( lus_i = 0; lus_i < lusaddsqrs
			/* and maxbreedte niet overschreden
			   !!!!!!!!!!!!!
			 */
			; lus_i++ ) {
			cop[ncop++] = 0;
			cop[ncop++] = 0x80; /* G */
			cop[ncop++] = 0x04; /* 5 */
			cop[ncop++] = 0;
			line_data.linebuf1[lnum   ] = '=';
			line_data.linebuf2[lnum++ ] = ' ';
			line_data.line_nr++ ;
			line_data.wsum +=
			   ((float) ( 9 * central.set) ) / 5184.;
		     }
		  }
	       }
	       break;
	    case 'C' :  /* end line here */
	       /* ^CR  =  end line here  */
	       switch ( luscx ) {
		  case 'R' :
		     margin (central.inchwidth - line_data.wsum, 1 );
		     break;
		  case 'L' :
		     margin ((central.inchwidth - line_data.wsum)*.5 , 0 );
		     margin ((central.inchwidth - line_data.wsum)*.5 , 1 );
		     break;
	       }

	       /* ^CL  = place text in center line
		  -> central placement of the text in the line
		*/
		  break;
	    case 'E' :  /* EOF reached */
	       margin (central.inchwidth - line_data.wsum, 1 );
	       break;

	    case 'F' : /* ^Fn -> '_' =>
			   fixed spaces = 3 + n * .25  points
			      n = alpha-hexadicimaal  0123456789abcdef
			   */
	       datafix.wsp = 3 + alphahex( luscx ) * .25 ;
	       central.fixed = 'y';
	       fixed_space();
	       break;
	    case 'l' :  /* ^ln -> length ligatures his line
			      line_data.nlig
			      1, 2, 3
			    */
	       line_data.nlig = ( luscx > '0' && luscx < '4' ) ?
				  luscx - '0' :  3;
	       break;
	    case '8' :  /* insert ascII-code on its place  */
	    case '9' :
	    case 'a' :
	    case 'b' :
	    case 'c' :
	    case 'd' :
	    case 'e' :
	    case 'f' :
	       readbuffer[t3j  ] = 1 ; /* will be ignored later */
	       readbuffer[t3j+1] = 1 ; /* will be ignored */
	       readbuffer[t3j+2] = 16 * alphahex( luscy ) + alphahex( luscx );
	       t3j --;
	       break;

	 }  /* switch ( readbuffer[t3j+1] ) = luscy */

	 t3j += 3;
	 break;
      case '\015' :  /* carriage return */

	 if (line_data.para == 0) {  /* poems : fill the line */
	    margin (central.inchwidth - line_data.wsum, 1 );
	    t3j++;
	 } else {   /* flat text : ignore */
	    readbuffer[t3j]=' ';
	    t3j--;
	 }
	 break;
      case ' ' :              /* variable space set < 12: GS2, */
	 move(t3j,1);    /* store results */

	 if (central.set <= 48 ) {
	    line_data.wsum +=
		      ( (float) (wig[1] * central.set) ) / 5184. ;
	    cop[ncop++] = 0;
	    cop[ncop++] = 0xa0; /* GS */
	    cop[ncop++] = 0x02; /* 2  */
	    cop[ncop++] = 0;
	 } else {             /* set > 12: GS1  */
	    line_data.wsum +=
		      ( (float) ( wig[0] * central.set) ) / 5184. ;
	    cop[ncop++] = 0;
	    cop[ncop++] = 0xa0; /* GS */
	    cop[ncop++] = 0x40; /*  1 */
	    cop[ncop++] = 0;
	 }
	 plaats[lnum] = t3j;
	 plkind[lnum] = kind;
	 line_data.nspaces ++;
	 line_data.curpos ++;
	 line_data.linebuf1[lnum  ] = ' ';
	 line_data.linebuf2[lnum++] = ' ';
	 line_data.line_nr ++;
	 t3j++;
	 break;
      case '_' : /* add code for fixed spaces */
	 move(t3j,1);
	 plaats[lnum] = t3j;
	 plkind[lnum] = kind;
	 if (line_data.para == 0) {
	    for ( lus_k=0; lus_k<12; lus_k++ )
	       cop[ncop++] = datafix.code[lus_k];
	    line_data.wsum +=
		  (datafix.wunits * (float) central.set ) / 5184.;
	    line_data.nfix ++;

	    line_data.linebuf1[lnum  ] = '_';
	    line_data.linebuf2[lnum++] = ' ';
	    line_data.line_nr ++;
	 } else { /* line_data.para == 1 */
	    if (central.set <= 48 ) {
	       line_data.wsum +=
		      ( (float) (wig[1] * central.set) ) / 5184. ;
	       cop[ncop++] = 0;
	       cop[ncop++] = 0xa0; /* GS */
	       cop[ncop++] = 0x02; /* 2  */
	       cop[ncop++] = 0;
	    } else {             /* set > 12: GS1  */
	       line_data.wsum +=
		      ( (float) ( wig[0] * central.set) ) / 5184. ;
	       cop[ncop++] = 0;
	       cop[ncop++] = 0xa0; /* GS */
	       cop[ncop++] = 0x40; /*  1 */
	       cop[ncop++] = 0;
	    }
	    plaats[lnum] = t3j;
	    plkind[lnum] = kind;
	    line_data.nspaces ++;
	    line_data.linebuf1[lnum  ] = ' ';
	    line_data.linebuf2[lnum++] = ' ';
	    line_data.line_nr ++;
	 }
	 line_data.curpos ++;
	 t3j++;
	 break;
      default :
	 lus_k = line_data.nlig + 1;
	 do {    /* seek all ligatures */
	    lus_k--;
	    for ( lus_i=0; lus_i< 4; lus_i++ ) lus_ll[lus_i] = '\0';
	    for ( lus_i=0; lus_i< lus_k; lus_i++ ) {
	       lus_ll[lus_i] = readbuffer[t3j+lus_i];
	    }
	    uitkomst = zoek( lus_ll, line_data.kind, matmax);
	 }
	    while ( (uitkomst == -1) && (lus_k > 1) ) ;

	 if ( uitkomst == -1 ) {  /* no char found */
	    lus_k = 1;
	    uitkomst = 76; /* g5 is cast */
	    lus_ll[0]=' ';
	 }

	 move(t3j,lus_k);

	 for (lus_i=0;lus_i<lus_k;lus_i++) {  /* store ligature in linebuffer */
	    plaats[lnum] = t3j;
	    plkind[lnum] = kind;
	    line_data.linebuf1[lnum   ] =  lus_ll[lus_i];
	    switch (kind) {
	       case 0 : line_data.linebuf2[lnum ] = ' ' ;
		  break;
	       case 1 : line_data.linebuf2[lnum ] = '/' ;
		  break;
	       case 2 : line_data.linebuf2[lnum ] = '.' ;
		  break;
	       case 3 : line_data.linebuf2[lnum ] = ':' ;
		  break;
	    }
	    lnum++;
	    line_data.line_nr++;
	    t3j++;
	 }

	 lus_bu = (float) matrix[ uitkomst ].w;
	 lus_cu = matrix[uitkomst].mrij;
	 lus_du = matrix[uitkomst].mkolom;

	 if ( line_data.add  > 0 ) {
	    lus_bu += line_data.letteradd;
	    if ( line_data.add == 1 ) {
		 lusaddw = 0.;
		 line_data.letteradd = 0;
	    }
	    line_data.add --;
	 }

	 line_data.wsum += gen_system ( lus_du, /* column */
					lus_cu, /* row  */
					lus_bu  /* width char */
				       );

	 lus_i=0;      /* store generated code */
	 do {
	    cop[ ncop++ ] = cbuff[lus_i++];
	 }
	    while  (cbuff[lus_i] < 0xff);
      break; /* default */
   } /* end switch ctest */


      /*
      lus_k = 0;
      for (lus_i=0; lus_i< ncop ; ) {
	 letter[0] = cop[lus_i++]; letter[1] = cop[lus_i++]; letter[2] = cop[lus_i++];
	 letter[3] = cop[lus_i++]; lus_k ++;
	 print_at(20,1,"");     printf("code %3d ",lus_k);
	 dispcode( letter );
	 ce();
      }
      */

   disp_schuif(  );

   if (lnum>=10) {
	 print_at(22,1,"plt plknd ");
	 for (lus_i = lnum-10; lus_i<lnum; lus_i++)
	    printf(" %4d %1d", plaats[lus_i],plkind[lus_i]);
	 print_at(23,1,"lnum    = ");
	 for (lus_i = lnum-10; lus_i<lnum; lus_i++)
	    printf("  %4d ", lus_i);
	 print_at(24,1,"rb[pl[lus_i]] ");
	 for (lus_i= lnum-10; lus_i<lnum; lus_i++)
	    printf("     %1c ",readbuffer[plaats[lus_i]]);
   }

   calc_maxbreedte ( );

	 /* inwin ruimte spaties - mogelijkheid afbreekteken */
	 /*
	 print_at(22,1,"nspaces ");
	 printf("%2d ",line_data.nspaces);
	 print_at(23,1,"wsum: "); printf("%10.5f maxbreedte = %10.5f line = %10.5f ",
	    line_data.wsum,  maxbreedte, central.inchwidth );
	 */

   return ( t3j - lus_geb) ;
} /* lus readbuffer2  wsum */


/*
   translate  reverse[] to monotype code
 */

void translate( unsigned char c, unsigned char com )
{
   for ( trns_i=0;trns_i<4;trns_i++) revcode[trns_i] = 0;

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
	 trns_vt = 0;
	 if ( c > '0' && c <= '9' ) {
	    trns_vt = c - '0';
	 }
	 if ( c >= 'a' && c <='f' ) {
	    trns_vt = c - 'a' + 10;
	 }
	 if (trns_vt > 0 ) {
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
	    revcode[2] |= rijcode[trns_vt-1][2];
	    revcode[3] |= rijcode[trns_vt-1][3];
	 }
	 break;
   }

}   /* translate */



/*
      void margin  ( float length, unsigned char strt )

      length in: inches

      lnum = number of codes stored already

      strt = 0: beginning line
      strt = 1: end of the line
      strt = 2: in the middle of a line

   version 29-02-2004
   version  3-03-2004
      added: possibility of empty lines
   version 12-03-2004
      all intern variables global


      fill_line ( units_last );
      keer_om()
      translate( reverse[j] , com );
 */

void  margin(  float length, unsigned char strt )
{
    mar_units   = (int) (.5 + ( length * 5184. / (float) central.set ) );
    mar_totunit = (int) (.5 + ( line_data.wsum * 5184. / (float) central.set ) );


    if (central.set < 49 ) {
       mar_maxsub = (float) (line_data.nspaces * 2 * central.set);
    }  else {
       mar_maxsub = (float) (line_data.nspaces * central.set);
    }

    mar_maxsub /= 5184.;
    mar_subu = (int) (.5 + ( mar_maxsub * 5184. / (float) central.set ) );

    if ( line_data.wsum - mar_maxsub > central.inchwidth ) {
       p_error("line too width in function margin ");
    }

    fill_line ( mar_units );

    mar_nr = keerom();

    /* if ('#'==getchar()) exit(1); */


    for (mar_j=0; mar_j< mar_nr; mar_j++)
    {
       mar_com = '0';
       if ( strt == 0 ) {
	  if ( ( reverse[mar_j] >  '0' && reverse[mar_j] <= '9') ||
	       ( reverse[mar_j] >= 'a' && reverse[mar_j] <= 'f') ) {
	     if ( ( mar_nr - mar_j ) <= 2 ) {
		mar_com = (mar_j == (mar_nr-1) )  ? '2' : '1';
	     } else {
		mar_com = (mar_j == 0) ? '1': '2';
	     }
	  }
       } else { /* strt == 1 */
	  if ( ( reverse[mar_j] >  '0' && reverse[mar_j] <= '9') ||
	       ( reverse[mar_j] >= 'a' && reverse[mar_j] <= 'f') ) {
	     if ( ( mar_nr - mar_j ) <= 2 ) {
		mar_com = ( mar_j == ( mar_nr-1 ) )  ? 'b' : 'a';
	     } else {
		mar_com = ( mar_j == 0 ) ? 'a': 'b';
	     }
	  }
       }

       translate( reverse[mar_j] , mar_com );

       switch ( reverse[mar_j] ) {
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
       for (mar_k=0; mar_k<4; mar_k++)
	     cop[ncop++] = revcode[mar_k];
    }

    /*
	dit gaat naar de aanroepende functions
	if (line_data.vs > 0 ) {
	   if ( strt == 0 ) {
	      if (line_data.vs == 1) line_data.last = 0;
	      line_data.vs --;
	   }
	}
    */

    line_data.wsum    += length;
    line_data.line_nr =  lnum;
    end_line = strt;

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

    void fill_line(  unsigned int u )
	adjust ( int , float  );
	void  calc_kg ( int n )
    28 feb:   float adjust  ( int, float );
	void store_kg( void )
	int  iabsoluut( int )
	verdeel ( )

    12 maart: all variables global

*/

void fill_line(  unsigned int u )
{
      /*
      qadd = number of 9 unit spaces, that could fill the line
      var  = number of variable spaces used to fill out the line
       */

     for ( fill_i = 2 ; fill_i<100 ;fill_i++ ) verdeelstring[fill_i]=0;

     idelta = u ;

     fill_casus = 0;
     if (idelta >=3 ) fill_casus ++;
     if (idelta >=8 ) fill_casus ++;
     if (idelta >=17) fill_casus ++;
     if (idelta >=24) fill_casus ++;

     switch (fill_casus)
     {
	case 0 :
	   if (line_data.nspaces == 0 ) /* no variable spaces */
	   {
	      if ( line_data.nfix > 0 ) {  /* fixed spaces */
		 verdeelstring[fill_n++] = ( datafix.u2 > 9 ) ?
			 datafix.u2 + 'a'-10 : datafix.u2 + '0';
		 verdeelstring[fill_n++] = ( datafix.u1 > 9 ) ?
			 datafix.u1 + 'a'-10 : datafix.u1 + '0';
	      } else {          /* neither kind of spacing */
		 verdeelstring[0]='8'; /* nothing */
		 verdeelstring[1]='3';
	      }
	   } else {       /* variable spaces  */
	      if ( idelta < 0 ) {

		 if ( line_data.nspaces * 2 < iabsoluut(idelta) ) {
		    printf("line too wide in: fill_line() \n");
		    printf(" idelta = %4d var spaces = %3d ",idelta,line_data.nspaces);
		    getchar();
		    exit(1);
		    /* the adjustment wedges cannot cope with this */
		    /* minimum correction = 1/1 = -.0185" */
		 } else { /*  2 svp > iabs( idelta )
		       the adjustment wedges can still cope with this
		       situation, result a flat line...
			   */
		    calc_kg ( line_data.nspaces );
		    store_kg( );
		 }
	      } else {
		 calc_kg ( line_data.nspaces );
		 store_kg( );
	      }
	   }
	   break;
	case 1 :  /* >=4 <= 8  idelta == positive */
	   if ( line_data.nspaces < 3 ) {
	      var = 1;
	      adjust    ( wig[0], (float) (idelta-5)/(float) (1+line_data.nspaces) );
	      store_kg( );
	      verdeelstring[2] = 'v' ; /* GS1 */
	   } else {
	      calc_kg ( line_data.nspaces );
	      store_kg( );
	   }
	   break;
	case 2 :  /* > 8 <= 17 */
	   if ( line_data.nspaces < 3 ) {
	      radd = idelta - 9 ;
	      var = 1;
	      adjust( wig[4], ( (float) radd) / ( (float) (var+line_data.nspaces) ) );
	      store_kg( );
	      verdeelstring[2] = 'V' ; /* GS5 */
	   } else { /* flat filled line */
	      calc_kg ( line_data.nspaces );
	      store_kg( );
	   }
	   break;
	case 3 :  /* > 17 < 24 */
	   if ( line_data.nspaces < 3 ) {
	      radd = idelta - 18 ;
	      var = 2;
	      adjust ( wig[4], ((float) radd)/ ((float)(var+line_data.nspaces) ) );
	      store_kg( );
	      verdeelstring[2] = 'V' ; /* GS5 */
	      verdeelstring[3] = 'V' ;
	   } else {  /* flat filled line */
	      calc_kg ( line_data.nspaces );
	      store_kg( );
	   }
	   break;
	case 4 :  /* >= 24 */
	   var = 3;
	   qadd = idelta / 9;
	   radd =  ( idelta >=  27  ) ? idelta % 9 : idelta - 27 ;
	   adjust ( wig[4], ((float) radd)/((float) (var+line_data.nspaces) ) );
	   store_kg( );
	   fill_n = verdeel( );
	   if ( (line_data.nfix > 0) && (line_data.nspaces == 0) ) {
		 verdeelstring[fill_n++] = ( datafix.u2 > 9 ) ?
			 datafix.u2 + 'a'-10 : datafix.u2 +'0';
		 verdeelstring[fill_n++] = ( datafix.u1 > 9 ) ?
			 datafix.u1 +'a' -10 : datafix.u1 +'0';
	   }
	   break;
     }
}  /* fill_line  */



/*
   testzoek3:
   version 12 mrt

 */


char     t3ctest;
char     tz3cx, tz3c;
int      t3i;
int      opscherm;
int      t3key;
unsigned char inword;
unsigned char t3terug, t3t, endstr ;
int      loop2start;
int      zoekk;
int      t3rb1;




int testzoek3( char buf[] )
{

   t3t= 0;


   t3i = 0;  /* concatenate strings */
   while ( buf[t3i] != '\0' && nreadbuffer < 200 ) {
       readbuffer[nreadbuffer++] = buf[t3i++];
   }
   readbuffer[nreadbuffer]='\0';

   nschuif = 0;

   /* tzint1(); */

   cls();

   lusaddw   = 0.;  /* default = 0 */
   opscherm  = 0;
   ncop      = 0;   /* initialize line_data */

   clear_lined();

   lnum = 0;
   if (line_data.vs > 0 ) {
       if (line_data.last > central.inchwidth) {
	  line_data.last = central.inchwidth;
       }
       line_data.wsum = line_data.last;
       margin( line_data.last, 0 );
   }

   print_at(2,1,"Na margin ");
   printf("line_data.wsum %8.5f maxbr %8.5f ",
	   line_data.wsum,maxbreedte);
   if ('#'==getchar()) exit(1);

   calc_maxbreedte ( );


   /* tzint2( maxbreedte ); */

   for (t3i=0; t3i<200; t3i++) {
       plaats[t3i]=0; plkind[t3i] = 0;
   }


   for (t3j=0 ; t3j < 120
	     && (t3ctest = buf[t3j]) != '\015'/* cr = 13 dec */
	     && t3ctest != '\012'              /* lf = 10 dec */
	     && t3ctest != '\0'               /* end of buffer */
	     && line_data.wsum   < maxbreedte  ; )
   {
       print_at(5,1,"             ");
       print_at(5,1,"t3j ="); printf("%3d = %3x %1c",t3j,t3ctest,t3ctest);
       ce();

       lus ( t3ctest );

   }

   print_at(8,1,"na de for-lus ");
   printf("t3ctest = %3x %3d %1c ",t3ctest,t3ctest,t3ctest);

   ce();



   switch (t3ctest) {
      case '\015' :  /* cr= 13 dec    */
	 margin(central.inchwidth - line_data.wsum, 1 );
	 line_data.wsum = central.inchwidth;
	 t3j++;
	 break;
      case '\012' :  /* lf= 10 dec  nothing   */
	 t3j++;
	 break;
      case '\0'   :  /* end paragraph  */
	 t3j++;
	 break;
      default :
	 for ( t3i=0; t3i<lnum ; t3i++) {
	    print_c_at( 6, t3i+1 , line_data.linebuf1[t3i] );
	    print_c_at( 7, t3i+1 , line_data.linebuf2[t3i]);
	 }
	 /*
	 for ( t3i=75; t3i<150 ; t3i++) {
	    if ( line_data.linebuf1[t3i] != '\0') {
	       print_c_at(10, t3i+1 , line_data.linebuf1[t3i]);
	       print_c_at(11, t3i+1 , line_data.linebuf2[t3i]);
	    }
	 }
	  */
	 if ( line_data.line_nr < 75 )
	       print_at(8,line_data.line_nr   ,"^ ");
	 else
	       print_at(12,line_data.line_nr-75,"^ ");

	 t3terug = 0;   /* lnum */
	 t3t    = 0;
	 t3key   = 0;
	 do {
	    if (t3key != 79 ) {
	       do {
		  while ( ! kbhit() );
		  t3key = getch();
		  if( (t3key == 0) || (t3key == 0xe0) ) {
		     t3key = getch();
		  }
	       }
		  while ( t3key != 79 && t3key != 75 && t3key != 27 ) ;
	    }
	    tz3cx  = line_data.linebuf1[ line_data.line_nr - 1 ];
	    t3rb1 = line_data.linebuf1[ line_data.line_nr - 2 ];
	    /*
	     print_at(11,1,"tz3cx ");
	     printf("= %1c rb1 = %1c ",tz3cx,t3rb1);
	    */

	    inword = ( tz3cx != ' ' && tz3cx != '_' &&
		       t3rb1 != ' ' && t3rb1 != '_'  ) ;

	    /*
	     printf( inword ? " inword = true " : "inword = false ");
	     printf("j = %3d nsch %2d ",j,nschuif);
	    */
	    if (tz3cx == '_' ) {
	       line_data.nfix --;
	       line_data.wsum = schuif[nschuif-1];
	       ncop  = pcop[nschuif-1];
	       line_data.line_nr --;
	       /* disp_vsp(tz3cx); */

	       t3key = 79;   /* no need to wait for input */
	    }

	    if (tz3cx == ' ') {
	       line_data.nspaces --;
	       line_data.wsum = schuif[nschuif-1];
	       line_data.line_nr --;
	       ncop  = pcop[nschuif-1];
	       /* disp_vsp(tz3cx);*/
	       t3key = 79;   /* no need to wait anymore   */
	    }
	    switch (t3key) {
	       case 79 : /* regel afsluiten */
		/* in a word */

		  if ( tz3cx != ' ' && tz3cx != '_' /* een letter  */ ) {
		     /* add division */

		     endstr = plaats[lnum-2-t3t]+1;
		     print_at(11,1,"                                             ");
		     print_at(11,1,"NO SPACE ");
		     loop2start = plrb[nschuif-2]+ligl[nschuif-2];

		     printf("ns-1 = %3d  t3t %2d pl[lnum-t3t-2]+1 = %3d %3d ",
			nschuif-1, t3t , endstr ,loop2start
			);
		     if ('#'==getchar()) exit(1);




		     for (t3i=endstr; readbuffer[t3i] !='\0' && t3i<200 ; t3i++) {
			readbuffer2[t3i-endstr ] = readbuffer[t3i];
		     }
		     readbuffer2[t3i]='\0';
		     readbuffer[endstr   ]='-';
		     readbuffer[endstr+1 ]='\015';
		     readbuffer[endstr+2 ]='\012';
		     readbuffer[endstr+3 ]='\0';
		     line_data.linebuf1[line_data.line_nr]  ='-';
		     line_data.linebuf2[line_data.line_nr++]=' ';
		     print_at(14,1,"                                             ");
		     print_at(14,1,"");
		     printf(" ncop %4d wsum %8.5f ",pcop[nschuif-1],schuif[nschuif-1]);
		     /* herstellen soort letter */
		     zoekk = plaats[lnum-t3t-2]+1;
		     while (zoekk > plrb[nschuif-1]){
			zoekk--;
			print_at(15,1,"");
			printf("plkind[zoekk] =%3d ",plkind[zoekk]);
			if ('#'==getchar()) exit(1);
		     }
		  } else {  /* een spatie */
		     endstr = plaats[lnum-1-t3t] + 1;
		     for (t3i=endstr; readbuffer[t3i] !='\0' && t3i<200 ; t3i++) {
			readbuffer2[t3i-endstr ] = readbuffer[t3i];
		     }
		     readbuffer2[t3i]='\0';
		     print_at(14,1,"                                             ");
		     print_at(14,1,"NO SPACE ");
		     printf("ns-1 = %3d  t3t %2d pl[lnum-t3t-1] = %3d char=%1c",
			nschuif-1, t3t , endstr-1, readbuffer[endstr] );
		     readbuffer[endstr-1]='\015';
		     readbuffer[endstr]='\012';
		     readbuffer[endstr+1]='\0';
		     if ('#'==getchar()) exit(1);
		  }
		  break;
	       case 75 : /* move cursor */
		  if (t3t < 10 ) {
		     if ( ! ( tz3cx == ' ' || tz3cx == '_') ) {
			t3t ++;
			t3terug++;
			if (t3terug == ligl[nschuif-1] ) {
			   nschuif --;
			   t3terug = 0;
			}
			if ( line_data.line_nr < 75 )
			   print_at(8,line_data.line_nr   ,"  ");
			else
			   print_at(8,line_data.line_nr-75,"  ");
			line_data.line_nr --;
			if ( line_data.line_nr < 75 )
			   print_at(8,line_data.line_nr   ,"^");
			else
			   print_at(8,line_data.line_nr-75,"^");

			print_at(10,1,"");
			printf(" ns %2d t3t %2d lnum %3d ptr %3d plaats %3d tz3cx %1c ",
			    nschuif,t3t,lnum, (lnum-t3t-1) , plaats[lnum-t3t-1],
			    readbuffer[plaats[lnum-t3t-1]]
			    );

		     }
		  } else {
		     t3key = 79;
		  }
		  break;
	       case 27 : /* wil u werkelijk stoppen */
		  do {
		     print_at(3,1,"Do you really wonna quit ? ");
		     tz3c = getchar();
		  }
		    while ( tz3c != 'n' && tz3c != 'y' && tz3c != 'j' );
		  if ( tz3c != 'n' ) exit(1);
		  break;
	    }
	 }
	    while (t3key != 79 );   /* lnum */
	 line_data.wsum = schuif[nschuif-1];


	 /* soms niet soms wel */

	 for (t3j=loop2start ; t3j < endstr
		&& (t3ctest = readbuffer[t3j]) != '\015'  /* cr = 13 dec */
		&& t3ctest != '\012'  /* lf = 10 dec  */
		&& t3ctest != '\0'    /* end of buffer */
		&& line_data.wsum    < maxbreedte  ; )
	 {
	    lus ( t3ctest );
	 }
	 margin (central.inchwidth - line_data.wsum, 1 );
	 line_data.wsum = central.inchwidth;
	 break;
   }



   printf("Nu stoppen "); ce();



   /* line_data. */




   /* preserve the unused chars in read buffer */


   for (t3i=0;t3i<80;t3i++) print_c_at(4,t3i,' ');
   print_at(1,1,"");

   for (t3i=0; t3i< 80 ; t3i++) printf("%1c",readbuffer[t3i]);

   for (t3i=0;t3i<80;t3i++) print_c_at(5,t3i,' ');
   print_at(3,1,"");
   for (t3i=0; t3i<80 ; t3i++)  printf("%1c",readbuffer2[t3i]);

   for (t3i=0;t3i<80;t3i++) print_c_at(6,t3i,' ');
   print_at(4,1,"");
   for (t3i=0; t3i<80 ; t3i++)
      printf("%1c",buf[t3i]);


   if ('#'==getchar()) exit(1);




   /*
   print_at(3,1,"");
   printf("nrb=%3d wsum %8.5f varsp %2d fixsp %2d ",
	       nreadbuffer, line_data.wsum,
		 line_data.nspaces,  line_data.nfix );
    */

   print_at(4,1,"");
   for (t3i=0;t3i<nreadbuffer;t3i++)
     printf("%1c",readbuffer[t3i]);
   print_at(5,1,"");

   printf(" leave testzoek3 t3j = %3d ",t3j);


   if ('#'==getchar()) exit(1);


   return( t3j ); /* niet meer nodig t3j = global ... */

}  /* testzoek3  */



