/*
kbhit
 */

/* KBHIT.C illustrates:
 *      kbhit
 */

/* GETCH.C illustrates how to process ASCII or extended keys.
 * Functions illustrated include:
 *      getch           getche
 */

#include <conio.h>
#include <ctype.h>
#include <stdio.h>
#include <graph.h>


int key, key1; int asc;

void testkey();

void testkey()
{
	while ( ! kbhit() );

	/* If first key is 0, then get second extended. */

	key1 = getch();
	key  = key1;
	if( (key1 == 0) || (key1 == 0xe0) )
	{
	    key = getch(); asc = 0;
	}  /* Otherwise there's only one key. */
	else {
	    asc = 1;
	}
}


main()
{


    /* Read and display keys until ESC is pressed. */

    _clearscreen( _GCLEARSCREEN );


    while( 1 )
    {
	asc = 0;
	 _settextposition(1 ,5 );
	printf(" --->");

	testkey();


	if( (key1 == 0) || (key1 == 0xe0) )
	{
	    _settextposition(4, 5);
	    printf( "ASCII: no\tChar: NA\t  asc %3d                 ",asc );
	}

	/* Otherwise there's only one key. */
	else {
	   asc = 1;
	    _settextposition(4, 5);
	   printf( "ASCII: yes\tChar: %c \t asc %3d              ",
		  isgraph( key1 ) ? key1 : ' ', asc );
	}


	_settextposition(6, 5);
	printf( "Decimal: %d\tHex: %X\n", key, key );

	/* Echo character response to prompt. */
	if( key == 27)
	{
	   _settextposition(8, 5);
	    printf( "Do you really want to quit? (Y/n) " );
	    key = getche();
	    printf( "\n" );
	    if( (toupper( key ) == 'Y') || (key == 13) )
		break;
	}
    }

}



main1()
{
    /* Display message until key is pressed. */
    while( !kbhit() )
	cputs( "Hit me!! " );
    getch();
    /* Use getch to throw key away. */
    getch();
}

