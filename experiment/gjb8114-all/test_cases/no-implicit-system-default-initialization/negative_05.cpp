struct Counter
{
    static int value;
};

int Counter::value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-2]

int main()
{
    Counter::value = Counter::value + 1;
    return 0;
}
