typedef struct
{
    signed short d01 : 2;
    unsigned short d02 : 2;
    unsigned short res : 12;
} sData;

int main(void)
{
    sData my_data{};
    my_data.d01 = 1;
    my_data.d02 = 1;
    my_data.res = 0;
    return 0;
}
