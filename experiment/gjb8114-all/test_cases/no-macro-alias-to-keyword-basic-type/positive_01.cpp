#define JUDGE_ZERO(i) if (0 == (i))
typedef long int64;

int main()
{
    int64 i = 0;
    JUDGE_ZERO(i)
    {
        i = 1;
    }
    return 0;
}
