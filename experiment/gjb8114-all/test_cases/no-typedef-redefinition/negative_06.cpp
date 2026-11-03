typedef int mytype;

int main()
{
    auto make_value = []()
    {
        typedef float mytype; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-3]
        mytype value = 2.5f;
        return value;
    };

    auto result = make_value();
    return static_cast<int>(result);
}
