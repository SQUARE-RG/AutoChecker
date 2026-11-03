typedef struct
{
    unsigned long long d01 : 32;
    unsigned long long d02 : 32;
    int separator;
    unsigned long long d03 : 48;
    unsigned long long d04 : 16;
} stData;

int main(void)
{
    stData my_data;
    return (0);
}
