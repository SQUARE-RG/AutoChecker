typedef struct
{
    unsigned char d01 : 3;
    unsigned char d02 : 3;
    unsigned int marker;
    unsigned char d03 : 4;
    unsigned char d04 : 4;
} stData;

int main()
{
    stData my_data;
    return 0;
}
