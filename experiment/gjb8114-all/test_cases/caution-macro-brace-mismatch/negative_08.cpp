#define BEGIN_LAMBDA() [](int value) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-2]

int main()
{
    auto twice = BEGIN_LAMBDA()
        return value * 2;
    };

    return twice(3) == 6 ? 0 : 1;
}
