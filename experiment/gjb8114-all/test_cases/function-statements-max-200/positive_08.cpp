// Static member function with a small body, below the statement limit.
class SmallStaticFunction {
public:
    static int compute(int seed) {
        int value = seed;
        for (int i = 0; i < 3; ++i) {
            value += i;
        }
        if (value < 0) {
            value = -value;
        }
        return value;
    }
};

int main() {
    return SmallStaticFunction::compute(1);
}
