class Range {
public:
    int lowerBound;
    int upperBound;

    void setLower(int newLowerBound) {
        lowerBound = newLowerBound;
    }
};

int main() {
    Range r;
    r.lowerBound = 0;
    r.upperBound = 10;
    r.setLower(1);
    return r.lowerBound + r.upperBound;
}
