int threshold = 5;

class Calculator {
public:
    int compute(int threshold) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-2]
    {
        return threshold + 1;
    }
};

int main()
{
    Calculator calculator;
    return calculator.compute(2);
}
