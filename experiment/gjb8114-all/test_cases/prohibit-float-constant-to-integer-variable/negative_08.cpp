struct Holder
{
    int value;
};

int main()
{
    Holder holder{0};
    holder.value = 45.5; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-1]
    return holder.value;
}
