class Counter
{
public:
    int next()
    {
        ++value_;
        return value_;
    }

private:
    int value_ = 0;
};

int main()
{
    Counter counter;
    counter.next(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-11]
    return 0;
}
