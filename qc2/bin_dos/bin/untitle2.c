/* RECORDS2.C illustrates reading and writing of file records with the
 * following functions:
 *      fgetpos     fsetpos
 *
 * See RECORDS1.C for a version using fseek, rewind, and ftell.
''
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

#include <stdio.h>
#include <io.h>
#include <string.h>


/* File record */
struct RECORD
{
    int     integer;
    long    doubleword;
    double  realnum;
} filerec = { 0, 1, 10000000.0 };


/* RECORDS1.C illustrates reading and writing of file records using seek
 * functions including:
 *      fseek       rewind      ftell
 *
 * Other general functions illustrated include:
 *      tmpfile     rmtmp       fread       fwrite
 *
 * Also illustrated:
 *      struct
 *
 * See RECORDS2.C for a version of this program using fgetpos and fsetpos.
 */



/* File record */
struct RECORD1
{
    int     integer;
    long    doubleword;
    double  realnum;
    char    string[15];
} filerec1 = { 0, 1, 10000000.0, "eel sees tar" };

records1()
{
    int c, newrec;
    size_t recsize = sizeof( filerec1 );
    FILE *recstream;
    long recseek;

    /* Create and open temporary file. */
    recstream = tmpfile();

    /* Write 10 unique records to file. */
    for( c = 0; c < 10; c++ )
    {
	++filerec1.integer;
	filerec1.doubleword *= 3;
	filerec1.realnum /= (c + 1);
	strrev( filerec1.string );

	fwrite( &filerec1, recsize, 1, recstream );
    }

    /* Find a specified record. */
    do
    {
	printf( "Enter record betweeen 1 and 10 (or 0 to quit): " );
	scanf( "%d", &newrec );

	/* Find and display valid records. */
	if( (newrec >= 1) && (newrec <= 10) )
	{
	    recseek = (long)((newrec - 1) * recsize);
	    fseek( recstream, recseek, SEEK_SET );

	    fread( &filerec1, recsize, 1, recstream );

	    printf( "Integer:\t%d\n", filerec1.integer );
	    printf( "Doubleword:\t%ld\n", filerec1.doubleword );
	    printf( "Real number:\t%.2f\n", filerec1.realnum );
	    printf( "String:\t\t%s\n\n", filerec1.string );
	}
    } while( newrec );

    /* Starting at first record, scan each for specific value. The following
     * line is equivalent to:
     *      fseek( recstream, 0L, SEEK_SET );
     */
    rewind( recstream );

    do
    {
	fread( &filerec, recsize, 1, recstream );
    } while( filerec.doubleword < 1000L );

    recseek = ftell( recstream );
    /* Equivalent to: recseek = fseek( recstream, 0L, SEEK_CUR ); */
    printf( "\nFirst doubleword above 1000 is %ld in record %d\n",
	    filerec.doubleword, recseek / recsize );

    /* Close and delete temporary file. */
    rmtmp();
}

void random();
char readbuffer[80];

#define LIM 40

int  get_line();

int  get_line()
{
   int c,i,lim;

   i=0; lim = LIM;
   while ( --lim > 0 && (c=getchar()) != EOF && c != '\n')
      readbuffer[i++]=c;
   if (c=='\n') readbuffer[i++]=c;
   readbuffer[i]='\0';
   return(i);

}

void random()
{
    int n1,n2,number ;
    int N1, N2, ntot, tot;
    int nt1, nt2;

  do {

    N1=N2=ntot=0;
    do {
      printf(" geef eerste getal ");
      get_line();
      n1=atoi(readbuffer);
    } while (n1 <= 0 );
    do {
      printf(" geef tweede getal ");
      get_line();
      n2 = atoi(readbuffer);
      printf(" n1 = %3d n2 = %3d ",n1,n2);
    }
      while (n2 <= 0);
    tot = n1+n2;
    nt1 = n1;
    nt2 = n2;

    do {
      number = rand();
      number %= (n2+n1);
      printf("number = %3d ",number);
      if ( number <= n1 ) {
	 if (N1 < nt1 ) {
	    printf("rood  ");
	    N1++;
	    ntot++;
	    if (n1 > 0 ) n1--;
	 }
      }
      else {
	 if (N2 < nt2 ) {
	   printf("groen ");
	   N2++;
	   ntot++;
	   if (n2 > 0 ) n2--;
	 }
      }
      printf("\n");
      printf("n1 = %3d n2 = %3d ",n1,n2);
      printf("N1 = %3d N2 = %3d tot = %3d ",N1,N2,ntot);
      if ( getchar() == '#' )  break ;
    }
      while ( N1 < nt1 && N2 < nt2 /*ntot < tot - 1 */ );
    if ( n1 > 0 ) {
       do  {
	 N1++; ntot = N1 + N2;
	 printf("rood n1 %2d tot %3d ",N1,ntot);
	 getchar();
       }  while (N1 < nt1 );
    }
    if (n2 > 0 ) {
       do {
	  N2++; ntot = N1 + N2;
	  printf("groen n2 %2d tot %3d ",N2,ntot);
	  getchar();
       }  while (N2 <nt2 );
    }
    printf("doorgaan ? ");
  }
    while (getchar()!='#') ;
  exit(1);


}

main()
{
    int c, newrec;
    size_t recsize = sizeof( filerec );
    FILE *recstream;
    fpos_t *recpos;

    printf("waarom wil je niet linken ");
    getchar();
    random();

    records1();
    /* Create and open temporary file. */
    recstream = tmpfile();

    /* Write 10 unique records to file. */
    for( c = 0; c < 10; c++ )
    {
	++filerec.integer;
	filerec.doubleword *= 3;
	filerec.realnum /= (c + 1);

	fwrite( &filerec, recsize, 1, recstream );
    }

    /* Find a specified record. */
    do
    {
	printf( "Enter record betweeen 1 and 10 (or 0 to quit): " );
	scanf( "%d", &newrec );

	/* Find and display valid records. */
	if( (newrec >= 1) && (newrec <= 10) )
	{
	    *recpos = (fpos_t)((newrec - 1) * recsize);
	    fsetpos( recstream, recpos );
	    fread( &filerec, recsize, 1, recstream );

	    printf( "Integer:\t%d\n", filerec.integer );
	    printf( "Doubleword:\t%ld\n", filerec.doubleword );
	    printf( "Real number:\t%.2f\n", filerec.realnum );
	}
    }
	 while( newrec );

    /* Starting at first record, scan each for specific value. */
    *recpos = (fpos_t)0;
    fsetpos( recstream, recpos );
    do
    {
	fread( &filerec, recsize, 1, recstream );
    } while( filerec.doubleword < 1000L );

    fgetpos( recstream, recpos );
    printf( "\nFirst doubleword above 1000 is %ld in record %d\n",
	    filerec.doubleword, *recpos / recsize );

    /* Close and delete temporary file. */
    rmtmp();

}

