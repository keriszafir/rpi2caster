/* c:\qc2\stripc\monolus.c

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
      fixed_space();

   marge ( float length, unsigned char strt)

      commands in the input text-files:

      @00 = roman,
      @01 = italic
      @02 = small caps
      @03 = bold
      @04 = superieur

      @ln = length ligatures line_data.nlig n = 1, 2, 3
      @mx = next n lines start at lenght of this line
		    line_data.vs

      @pS = start paragraph
      @pE = End Paragraph

      kerning:

      @+n = add next char 1-9 units
      @-n = substract next char(s) 1/4 - 8/4 units
      @#x = add x * 18 units, if possible
      @=x = add x * 9 units, if possible

      @rx = repeat signal for kerning (x=alphahex) after: @+x && @-x


      End of line:

      @CR = Carriage Return: end line here
      @CC = place text in Center Line
      @CL = left filled line
      @CJ = line justified
      @CF

      ( @pE = line right alined )


      style:

      @Dx  = dominant color : 0-1
      @S0  = current style =  0
      @S1  = current style =  1
      @Sc  = current style alters




      @EF = end of file


      @Fx = '_' fixed spaces = 3 + x * .25  points
			      x = alpha-hexadicimaal  0123456789abcdef

      @vx = '_' fixed spaces set < 10



      @Lx = x empty lines  x = decimaal

      @Rx = repeat signal right margin
	       x = alphahex( )

      @Wx = width right margin
	    x = number of pica's/cicero's/fournier's (x=alphahex)


      @8x   insert ascII-code on its place
      @9x @ax @bx @cx @dx @ex @fx

      soep
      stoep
      koek


*/



int  lus( char ctest )
{

   lus_geb = t3j;

   switch ( ctest )
   {
      case '\00' :  /* ignore all control characters */
      case '\01' :
      case '\02' :
      case '\03' :
      case '\04' :
      case '\05' :
      case '\06' :
      case '\07' :
      case '\010':
      case '\011':
      case '\012':  /* linefeed = ignored */
      case '\013':
      case '\014':
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
      case '\015':  /* carriage return */
	 if (line_data.para == 0) {
	    t3j++;
	 } else {   /* flat text : ignore */
	    readbuffer[t3j]=' ';
	    t3j++; /* hier stond -- maak een spatie */
	 }
	 break;
		    /* \015 = 13 decimal = CR */

      case  '@' :  /* all commands  */
	 luscy = readbuffer[t3j+1];
	 luscx = readbuffer[t3j+2];

	 /*
	 print_at(12,1,"ctest =^ ");
	 printf(" t3j = %3d luscy = %1c luscx = %1c ",t3j,luscy,luscx);
	 if ('#'==getchar()) exit(1);
	  */

	 switch ( luscy )   /* readbuffer[t3j+1] */
	 {
	    case 'D' : /* dominant style */
	       central.d_style =  (luscx == 1) ? 1 : 0;
	    case 'S' : /* current style  */
	       switch (luscx) {
		  case '0' : line_data.c_style = 0; break;
		  case '1' : line_data.c_style = 1; break;
		  case 'c' :
		     if ( line_data.c_style == 1 )
			 line_data.c_style = 0;
		     else
			 line_data.c_style = 1;
		     break;
	       }
	       break;
	    case 'p' :  /* paragraph */
	       switch (luscx) {
		  case 'S' :   /* on */
		    line_data.para = 1;
		    break;
		  case 'E' :   /* off */
		    line_data.para = 0;
		    /* end of the paragraph: fill the line
		    */
		    marge ( central.inchwidth - line_data.wsum, 1);
		    break;
	       }
	       break;
	    case '0' :  /*  @00 = roman
			    @01 = italic
			    @02 = lower case to small caps
			    @03 -> bold
			    @04 -> superior chars
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
	    case 'm' :  /* @mn -> next n lines start at lenght
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
	    case '+' :  /* @+1 -> add next char 1-9 units
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
	    case '-' :  /* @-1 -> subtract 1-8 1/4 units
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
	    case '#' :  /* @#n add n times 18 units squares alpha-hex .... */

	       if ( ( line_data.wsum +
		    ( (float) (alphahex(luscx) * 18 * central.set) ) / 5184.)
		      > central.inchwidth ) {

		  marge (central.inchwidth - line_data.wsum, 1 );

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
	    case '=' :  /* @=n -> add n half squares alphahex... */

	       if ( ( line_data.wsum +
		      ((float) ( alphahex(luscx) * 9 * central.set ) ) / 5184.)
		      > central.inchwidth ) {

		  marge /*in*/ (central.inchwidth - line_data.wsum, 1 );

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

	       print_at(1,10,"eind regel");
	       printf(" lijn %12.4f \n",central.inchwidth);
	       printf(" text %12.4f \n",line_data.wsum);
	       if (getchar()=='#') exit(1);

	       switch ( luscx ) {
		  case 'L' : /* left centered */
		     marge ( central.inchwidth -line_data.wsum , 0 );
		     break;
		  case 'R' : /* right alined */
		     marge ( central.inchwidth - line_data.wsum, 1 );
		     break;
		  case 'C' : /* centered */
		     marge ( central.inchwidth - line_data.wsum, 2 );
		     break;
		  case 'F' : /* flat if possible */
		     marge ( central.inchwidth - line_data.wsum, 5 );
		     break;
		}

	       break;
	    case 'E' :  /* EOF reached */
	       printf("End wsum = %10.4f ",line_data.wsum);

	       marge /*in*/ (central.inchwidth - line_data.wsum, 1 );

	       t3j++; /* een verder zetten */
		 /* input file sluiten
		  rest wegschrijven naar output file
		  vlag zetten, zodat het programma stopt

		  */
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
	       /* the two next chars will not be evaluated a second time */

	       readbuffer[t3j  ] = '\00' ;
	       readbuffer[t3j+1] = '\00' ;
	       readbuffer[t3j+2] = 16*alphahex( luscy ) + alphahex( luscx );
	       t3j --;
	       break;

	 }  /* switch ( readbuffer[t3j+1] ) = luscy */

	 t3j += 3;
	 break;
      case ' ' :              /* variable space set <= 12: GS2, */
	 move(t3j,1);    /* store results */

	 if (central.set <= 48 ) {
	    line_data.wsum +=
		      ( (float) (wig[1] * central.set) ) / 5184. ;

	    cop[ncop++] = 0;
	    cop[ncop++] = 0xa0; /* GS */
	    cop[ncop++] = 0x20; /* 02 van 02 -> 20 6 aug 2004  */
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
	       cop[ncop++] = 0x20; /* 2  van 02 -> 20 6 aug 2004 */
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
}

/* lus readbuffer2  wsum */

