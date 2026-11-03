#define pabs(x) ((x) >= 0 ? (x) : -(x))

int main()
{
    unsigned int result;
    int a = 6;
    result = pabs(a) + 1;
    return 0;
}
