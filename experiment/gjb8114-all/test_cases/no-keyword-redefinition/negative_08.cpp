struct WideStreamHolder
{
    unsigned int wcout = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-4]
};

int main()
{
    WideStreamHolder holder;
    return static_cast<int>(holder.wcout);
}
