struct Holder
{
    short narrow;
};

int main()
{
    Holder h{};
    long wideValue = 0L;
    h.narrow = wideValue; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-2]
    return 0;
}
