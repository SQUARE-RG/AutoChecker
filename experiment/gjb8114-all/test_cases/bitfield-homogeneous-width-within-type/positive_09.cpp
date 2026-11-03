typedef signed char SmallBits;

typedef struct
{
    SmallBits a : 3;
    SmallBits b : 5;
} SmallData;

int main()
{
    SmallData data;
    return 0;
}
