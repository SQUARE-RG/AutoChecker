int main()
{
    auto compare = [](bool a, bool b) { return a > b; }; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-1]
    bool result = compare(true, false);
    return result ? 1 : 0;
}
