#include <algorithm>
#include <cstddef>

class Spectrum {
public:
    Spectrum() : values(new double[3]{0.0, 0.0, 0.0}), length(3) {}
    explicit Spectrum(const double (&samples)[3]) : values(new double[3]), length(3) {
        std::copy(samples, samples + 3, values);
    }
    Spectrum(const Spectrum& other) : values(new double[other.length]), length(other.length) {
        copyValues(other);
    }
    Spectrum& operator=(const Spectrum& other) {
        if (this != &other) {
            if (length != other.length) {
                delete[] values;
                values = new double[other.length];
                length = other.length;
            }
            copyValues(other);
        }
        return *this;
    }
    ~Spectrum() { delete[] values; }
private:
    void copyValues(const Spectrum& other) {
        std::copy(other.values, other.values + other.length, values);
    }
    double* values;
    std::size_t length;
};

int main() {
    Spectrum a;
    Spectrum b(a);
    a = b;
    return 0;
}
