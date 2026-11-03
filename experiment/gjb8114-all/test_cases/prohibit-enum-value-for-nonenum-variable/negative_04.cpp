int main()
{
    enum Marker { Zero = 0, One = 1, Two = 2 };
    double value;
    value = Two; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-11]
    return static_cast<int>(value - 2.0);
}
