#include "XMLParser.h"
#include <itksys/SystemTools.hxx>
#include <iostream>
#include <fstream>
#include <ElementContainer.h>
#include "BRAINSCutExceptionStringHandler.h"
static
void
SE(void *parser,
   const XML_Char *name,
   const XML_Char * *atts)
{
  XMLParser *Parser = static_cast<XMLParser *>( parser );

  Parser->StartElement(Parser->GetUserData(),
                       name,
                       atts);
}

static
void
EE(void *parser,
   const XML_Char *name)
{
  XMLParser *Parser = static_cast<XMLParser *>( parser );

  Parser->EndElement(Parser->GetUserData(),
                     name);
}

bool
XMLParser::Parse()
{
  this->m_Parser = XML_ParserCreate(0);

  XML_SetElementHandler(this->m_Parser,
                        &SE,
                        &EE);
  XML_SetUserData(this->m_Parser, this);

  std::ifstream inputstream;

  inputstream.open(this->m_Filename.c_str(), std::ios::binary | std::ios::in);
  if( inputstream.fail() )
    {
    std::string message = "Can't open ";
    message += this->m_Filename;
    message += '\n';
    BRAINSCutExceptionStringHandler exception(message);
    throw exception;
    }

  // Default stream parser just reads a block at a time.
  std::streamsize filesize =
    itksys::SystemTools::FileLength( this->m_Filename.c_str() );

  this->m_Buffer = new char[filesize];

  inputstream.read(this->m_Buffer, filesize);

  if( static_cast<std::streamsize>( inputstream.gcount() ) != filesize )
    {
    BRAINSCutExceptionStringHandler exception("File Read Error");
    throw exception;
    }
  return XML_Parse(this->m_Parser,
                   this->m_Buffer,
                   inputstream.gcount(),
                   true);
}
