void ontcijfer3()
{
    int ni,nj;

    for (ncode=0;ncode<36;ncode++) ontc[ncode]='0';

    for (ni = 0; ni<4 ; ni++) mono.code[ni]=mcx[ni];


    ncode=0;
    mcode[ncode++]=' ';

    /*
    printf("Gegoten        %5d : ",  gegoten);
     */

    if (mcx[0] & 0x80) { ontc[ 0]='1'; mcode[0]='O';       ni++; };
    if (mcx[0] & 0x40) { ontc[ 1]='1'; mcode[ncode++]='N'; ni++; };
    if (mcx[0] & 0x20) { ontc[ 2]='1'; mcode[ncode++]='M'; ni++; };
    if (mcx[0] & 0x10) { ontc[ 3]='1'; mcode[ncode++]='L'; ni++; };
    if (mcx[0] & 0x08) { ontc[ 4]='1'; mcode[ncode++]='K'; ni++; };
    if (mcx[0] & 0x04) { ontc[ 5]='1'; mcode[ncode++]='J'; ni++; };
    if (mcx[0] & 0x02) { ontc[ 6]='1'; mcode[ncode++]='I'; ni++; };
    if (mcx[0] & 0x01) { ontc[ 7]='1'; mcode[ncode++]='H'; ni++; };
    ontc[8]=' ';
    if (mcx[1] & 0x80) { ontc[ 9]='1'; mcode[ncode++]='G'; ni++; };
    if (mcx[1] & 0x40) { ontc[10]='1'; mcode[ncode++]='F'; ni++; };
    if (mcx[1] & 0x20) { ontc[11]='1'; mcode[ncode++]='S'; };
    if (mcx[1] & 0x10) { ontc[12]='1'; mcode[ncode++]='E'; ni++; };

    if (mcx[1] & 0x08) { ontc[13]='1'; mcode[ncode++]='D'; ni++; };
    if (mcx[1] & 0x04) { ontc[14]='1'; mcode[ncode++]='g'; ni++; };
    if (mcx[1] & 0x02) { ontc[15]='1'; mcode[ncode++]='C'; ni++; };
    if (mcx[1] & 0x01) { ontc[16]='1'; mcode[ncode++]='B'; ni++; };
    ontc[17]=' ';
    if (mcx[2] & 0x80) { ontc[18]='1'; mcode[ncode++]='A'; ni++; };
    if (ni == 0 && ! (mcx[3] & 0x01 )) mcode[0] ='O';
    if (ni == 2 ) {
       if (mcode[1] == 'N') {
	  if ( mcode[2] != 'I' && mcode[2] != 'L'
	       && mcode[2] != 'J'&& mcode[2] != 'K' ) {
	     printf("column-code incorrect.");
	     for (nj=0;nj<ncode;nj++){
		printf("%1c",mcode[nj]);
	     }
	     if (getchar()=='#') exit(1) ;
	  }
       } else {

       }

    }
    ni  = 0;
    if (mcx[2] & 0x40) { ontc[19]='1'; mcode[ncode++]='1'; ni++; };
    if (mcx[2] & 0x20) { ontc[20]='1'; mcode[ncode++]='2'; ni++; };
    if (mcx[2] & 0x10) { ontc[21]='1'; mcode[ncode++]='3'; ni++; };

    if (mcx[2] & 0x08) { ontc[22]='1'; mcode[ncode++]='4'; ni++; };
    if (mcx[2] & 0x04) { ontc[23]='1'; mcode[ncode++]='5'; ni++; };
    if (mcx[2] & 0x02) { ontc[24]='1'; mcode[ncode++]='6'; ni++; };
    if (mcx[2] & 0x01) { ontc[25]='1'; mcode[ncode++]='7'; ni++; };
    ontc[26]=' ';
    if (mcx[3] & 0x80) { ontc[27]='1'; mcode[ncode++]='8'; ni++; };
    if (mcx[3] & 0x40) { ontc[28]='1'; mcode[ncode++]='9'; ni++; };
    if (mcx[3] & 0x20) { ontc[29]='1'; mcode[ncode++]='a'; ni++; };
    if (mcx[3] & 0x10) { ontc[30]='1'; mcode[ncode++]='b'; ni++; };
    if (mcx[3] & 0x08) { ontc[31]='1'; mcode[ncode++]='c'; ni++; };
    if (mcx[3] & 0x04) { ontc[32]='1'; mcode[ncode++]='d'; ni++; };
    if (mcx[3] & 0x02) { ontc[33]='1'; mcode[ncode++]='e'; ni++; };
    if (ni == 0 ) mcode[ncode++]='f';
    if (mcx[3] & 0x01) { ontc[34]='1'; mcode[ncode++]='k'; };
    ontc[35]=' ';

    mcode[ncode]='\0';

    /*
    disp_bytes();
     */

    /*
    for (ni = 0; ni<36; ni++) printf("%1c",ontc[ni]);
    printf("     ");
    for (ni=0; ni<ncode; ni++) {
       if (mcode[ni] != ' ') printf("%c",mcode[ni]);
    }
    printf(" l %3d\n",regelnr);
    */

    if ( test_k() ) {
	  p0005 = test_row();
    }
    if ( test_g() ) {
	  p0075 = test_row();
    }
}

