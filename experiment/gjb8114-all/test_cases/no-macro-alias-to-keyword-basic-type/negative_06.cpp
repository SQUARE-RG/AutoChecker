#define CLASS class // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-2]

CLASS Widget
{
public:
    int value;
};

int main()
{
    Widget w{42};
    return w.value;
}
