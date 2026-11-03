namespace sample {

int scale = 10;

int apply(int scale) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-2]
{
    return scale * 2;
}

} // namespace sample

int main()
{
    return sample::apply(3);
}
