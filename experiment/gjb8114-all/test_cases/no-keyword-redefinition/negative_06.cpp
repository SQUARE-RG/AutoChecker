int main()
{
    auto increment = [](unsigned int cerr) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-4]
        return cerr + 1U;
    };

    return static_cast<int>(increment(0U));
}
