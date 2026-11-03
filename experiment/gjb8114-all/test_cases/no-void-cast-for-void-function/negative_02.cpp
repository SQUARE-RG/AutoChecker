class Counter {
public:
    void reset() { value = 0; }
private:
    int value = 0;
};

int main()
{
    Counter c;
    (void)c.reset(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-12]
    return 0;
}
