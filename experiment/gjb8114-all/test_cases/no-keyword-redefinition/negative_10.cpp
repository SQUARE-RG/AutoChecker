enum class WideStreamIndex
{
    wcerr = 0 // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-4]
};

int main()
{
    return static_cast<int>(WideStreamIndex::wcerr);
}
