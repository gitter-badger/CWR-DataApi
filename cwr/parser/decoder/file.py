# -*- coding: utf-8 -*-
import logging

from cwr.parser.decoder.common import GrammarDecoder
from config_cwr.accessor import CWRConfiguration
from cwr.grammar.factory.rule import FieldRuleFactory
from data_cwr.accessor import CWRTables
from cwr.grammar.factory.rule import DefaultRuleFactory
from cwr.grammar.factory.decorator import *
from cwr.parser.decoder.dictionary import *
from cwr.grammar.factory.adapter import *

"""
Classes for processing CWR files, creating a graph of CWR model instances from
it.

While the decoder classes are accessible, they are meant to be used directly
only for creating custom versions, by default the factory methods
default_file_decoder() and default_filename_decoder() should be used to acquire
the decoders to use when reading a file.

The default_file_decoder() will return a decoder which parses a CWR file
complying with the standard, while the default_filename_decoder() method will
return a decoder which parses a CWR filename which follows the old or the new
file naming convention.

The file decoder will also parse the filename, using the second parser for it,
and return a CWRFile instance. The filename decoder will return a FileTag.

The base classes used on these parsers are FileDecoder and FileNameDecoder,
both of them requiring information about the grammar to be used when parsing.
"""

__author__ = 'Bernardo Martínez Garrido'
__license__ = 'MIT'
__status__ = 'Development'


def _default_group_decoders():
    decoders = {}

    decoders['transmission'] = TransmissionDictionaryDecoder()
    decoders['group_info'] = GroupDictionaryDecoder()

    return decoders


def _default_record_decoders():
    decoders = {}

    decoders['acknowledgement'] = AcknowledgementDictionaryDecoder()
    decoders['message'] = MessageDictionaryDecoder()
    decoders['agreement'] = AgreementDictionaryDecoder()
    decoders['territory_in_agreement'] = AgreementTerritoryDictionaryDecoder()
    decoders['additional_related_information'] = \
        AdditionalRelatedInformationDictionaryDecoder()
    decoders['group_header'] = GroupHeaderDictionaryDecoder()
    decoders['group_trailer'] = GroupTrailerDictionaryDecoder()
    decoders['interested_party_agreement'] = \
        InterestedPartyForAgreementDictionaryDecoder()
    decoders['nra_agreement_party'] = \
        NonRomanAlphabetAgreementPartyDictionaryDecoder()
    decoders['nra_publisher_name'] = \
        NonRomanAlphabetPublisherNameDictionaryDecoder()
    decoders['nra_writer_name'] = NonRomanAlphabetWriterNameDictionaryDecoder()
    decoders['nra_title'] = NonRomanAlphabetTitleDictionaryDecoder()
    decoders['nra_performance_data'] = \
        NonRomanAlphabetPerformanceDataDictionaryDecoder()
    decoders['nra_work'] = NonRomanAlphabetWorkDictionaryDecoder()
    decoders['nra_other_writer'] = \
        NonRomanAlphabetOtherWriterDictionaryDecoder()
    decoders['publisher'] = PublisherRecordDictionaryDecoder()
    decoders['publisher_territory'] = IPTerritoryOfControlDictionaryDecoder()
    decoders['transmission_header'] = TransmissionHeaderDictionaryDecoder()
    decoders['transmission_trailer'] = TransmissionTrailerDictionaryDecoder()
    decoders['work'] = WorkDictionaryDecoder()
    decoders['work_conflict'] = WorkDictionaryDecoder()
    decoders['work_alternate_title'] = AlternateTitleDictionaryDecoder()
    decoders['entire_work_title'] = AuthoredWorkDictionaryDecoder()
    decoders['original_work_title'] = AuthoredWorkDictionaryDecoder()
    decoders['performing_artist'] = PerformingArtistDictionaryDecoder()
    decoders['recording_detail'] = RecordingDetailDictionaryDecoder()
    decoders['work_origin'] = WorkOriginDictionaryDecoder()
    decoders['instrumentation_summary'] = \
        InstrumentationSummaryDictionaryDecoder()
    decoders['instrumentation_detail'] = \
        InstrumentationDetailDictionaryDecoder()
    decoders['component'] = ComponentDictionaryDecoder()
    decoders['writer'] = WriterRecordDictionaryDecoder()
    decoders['writer_publisher'] = PublisherForWriterDictionaryDecoder()
    decoders['writer_territory'] = IPTerritoryOfControlDictionaryDecoder()
    decoders['filename_new'] = FileTagDictionaryDecoder()
    decoders['filename_old'] = FileTagDictionaryDecoder()

    return decoders


def default_adapters():
    adapters = {}

    adapters['alphanum'] = AlphanumAdapter()
    adapters['alphanum_ext'] = ExtendedAlphanumAdapter()
    adapters['numeric'] = NumericAdapter()
    adapters['boolean'] = BooleanAdapter()
    adapters['flag'] = FlagAdapter()
    adapters['date'] = DateAdapter()
    adapters['time'] = TimeAdapter()
    adapters['date_time'] = DateTimeAdapter()
    adapters['blank'] = BlankAdapter()
    adapters['lookup'] = LookupAdapter()
    adapters['iswc'] = ISWCAdapter()
    adapters['ipi_name_n'] = IPINameNumberAdapter()
    adapters['ipi_base_n'] = IPIBaseNumberAdapter()
    adapters['percentage'] = PercentageAdapter()
    adapters['ean13'] = EAN13Adapter()
    adapters['isrc'] = ISRCAdapter()
    adapters['visan'] = VISANAdapter()
    adapters['avi'] = AudioVisualKeydapter()
    adapters['charset'] = CharSetAdapter()
    adapters['alphanum_variable'] = VariableAlphanumAdapter()
    adapters['numeric_float'] = NumericFloatAdapter()
    adapters['year'] = YearAdapter()
    adapters['filename_version'] = FilenameVersionAdapter()
    adapters['lookup_int'] = LookupIntAdapter()

    return adapters


def default_grammar_factory():
    config = CWRConfiguration()

    data = config.load_field_config('table')
    data.update(config.load_field_config('common'))

    field_values = CWRTables()

    for entry in data.values():
        if 'source' in entry:
            values_id = entry['source']
            entry['values'] = field_values.get_data(values_id)

    factory_field = FieldRuleFactory(data, default_adapters())

    optional_decorator = OptionalFieldRuleDecorator(data, default_adapters())

    rules = _process_rules(config.load_record_config('common'))
    rules.update(_process_rules(config.load_transaction_config('common')))
    rules.update(_process_rules(config.load_group_config('common')))

    decorators = {'transaction_record': TransactionRecordRuleDecorator(
        factory_field,
        _default_record_decoders()
    ),
        'record': RecordRuleDecorator(
            factory_field,
            _default_record_decoders()
        ),
        'group': GroupRuleDecorator(_default_group_decoders())}
    return DefaultRuleFactory(
        rules,
        factory_field,
        optional_decorator,
        decorators
    )


def default_filename_grammar_factory():
    config = CWRConfiguration()

    data = config.load_field_config('table')
    data.update(config.load_field_config('common'))
    data.update(config.load_field_config('filename'))
    field_values = CWRTables()

    for entry in data.values():
        if 'source' in entry:
            values_id = entry['source']
            entry['values'] = field_values.get_data(values_id)

    factory_field = FieldRuleFactory(data, default_adapters())

    optional_decorator = OptionalFieldRuleDecorator(data, default_adapters())

    return DefaultRuleFactory(
        _process_rules(config.load_record_config('filename')),
        factory_field,
        optional_decorator
    )


def _process_rules(rules):
    processed = {}
    for rule in rules:
        rule_id = rule.id
        processed[rule_id] = rule

    return processed


def default_file_decoder():
    """
    Creates a decoder which parses a CWR file, creating a CWRFile class
    instance from it.

    :return: a CWR file decoder for the default standard
    """
    return FileDecoder(
        default_grammar_factory().get_rule('transmission'),
        default_filename_decoder()
    )


def default_filename_decoder():
    """
    Creates a decoder which parses CWR filenames following the old or the new
    convention.

    :return: a CWR filename decoder for the old and the new conventions
    """
    factory = default_filename_grammar_factory()

    grammar_old = factory.get_rule('filename_old')
    grammar_new = factory.get_rule('filename_new')

    return FileNameDecoder(grammar_old, grammar_new)


class FileDecoder(Decoder):
    """
    Parses a CWR file, both its contents and the file name, to create a CWRFile
     instance.

    As the CWRFile contains a FileTag, this decoder will also try to decode the
    file's name.

    For this it will use a second decoder, which will take care of the filename.
    """

    def __init__(self, grammar, filename_decoder):
        super(FileDecoder, self).__init__()

        # Logger
        self._logger = logging.getLogger(__name__)

        self._filename_decoder = filename_decoder
        self._file_decoder = GrammarDecoder(grammar)

    def decode(self, data):
        """
        Parses the file, creating a CWRFile from it.

        It requires a dictionary with two values:
        - filename, containing the filename
        - contents, containing the file contents

        :param data: dictionary with the data to parse
        :return: a CWRFile instance
        """
        file_name = self._filename_decoder.decode(data['filename'])

        file_data = data['contents']
        i = 0
        max_size = len(file_data)
        while file_data[i:i + 1] != 'H' and i < max_size:
            i += 1
        if i > 0:
            data['contents'] = file_data[i:]

        transmission = self._file_decoder.decode(data['contents'])[0]

        return CWRFile(file_name, transmission)


class FileNameDecoder(Decoder):
    """
    Parses a CWR filename to create a FileTag instance. It is meant to take
    care of the old and the new naming conventions, and so it will require one
    grammar rule for each.

    If the filename does not conform any of the two conventions, then an empty
    FileTag will be returned.
    """

    def __init__(self, grammar_old, grammar_new):
        super(FileNameDecoder, self).__init__()

        self._filename_decoder_old = GrammarDecoder(grammar_old)
        self._filename_decoder_new = GrammarDecoder(grammar_new)

    def decode(self, file_name):
        """
        Parses the filename, creating a FileTag from it.

        It will try both the old and the new conventions, if the filename does
        not conform any of them, then an empty FileTag will be returned.

        :param file_name: filename to parse
        :return: a FileTag instance
        """
        try:
            file_tag = self._filename_decoder_new.decode(file_name)
        except:
            try:
                file_tag = self._filename_decoder_old.decode(file_name)
            except:
                file_tag = FileTag(0, 0, '', '', '')

        return file_tag
