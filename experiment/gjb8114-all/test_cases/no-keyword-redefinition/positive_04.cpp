class Accumulator {
public:
    void add(int amount) { total += amount; }
    int value() const { return total; }

private:
    int total = 0;
};

int main()
{
    Accumulator accumulator;
    accumulator.add(5);
    return accumulator.value() == 5 ? 0 : 1;
}
