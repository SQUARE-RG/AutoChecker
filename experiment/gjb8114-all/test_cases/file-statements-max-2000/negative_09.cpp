#define TEN continue; continue; continue; continue; continue; continue; continue; continue; continue; continue;
#define HUNDRED TEN TEN TEN TEN TEN TEN TEN TEN TEN TEN
#define C continue;

void test()
{
    do
    {
        HUNDRED
        HUNDRED
        HUNDRED
        HUNDRED
        HUNDRED
        HUNDRED
        HUNDRED
        HUNDRED
        HUNDRED
        HUNDRED
        HUNDRED
        HUNDRED
        HUNDRED
        HUNDRED
        HUNDRED
        HUNDRED
        HUNDRED
        HUNDRED
        HUNDRED
        TEN
        TEN
        TEN
        TEN
        TEN
        TEN
        TEN
        TEN
        TEN
        C
        C
        C
        C
        C
        C
        C
        continue; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-2-1]
    } while (false);
}

int main()
{
    return 0;
}
