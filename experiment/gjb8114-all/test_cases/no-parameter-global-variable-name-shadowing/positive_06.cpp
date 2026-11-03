int threshold = 5;

class Calculator {
public:
    int compute(int value)
    {
        return threshold + value;
    }
};

int main()
{
    Calculator calculator;
    return calculator.compute(2);
}
