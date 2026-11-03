#include <iostream>

class Document {
public:
    int docid;
    Document() : docid(0) {}
    explicit Document(int v) : docid(v) {}
};

class Book : public Document {
public:
    int bookid;
    Book() try : bookid(1) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-5]
    {
    } catch (...) {
    }
};

int main() {
    Book mybook;
    std::cout << mybook.docid << mybook.bookid << std::endl;
    return 0;
}
