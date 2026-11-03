struct FloatHolder
{
    float value;

    void assign(double input)
    {
        value = input; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-3]
    }
};

int main()
{
    FloatHolder holder;
    holder.assign(2.5);
    return 0;
}
