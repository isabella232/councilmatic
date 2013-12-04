# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CouncilMemberAlias'
        db.create_table(u'phillyleg_councilmemberalias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(related_name='legislative_names', to=orm['phillyleg.CouncilMember'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'phillyleg', ['councilmemberalias'])

        # Adding field 'CouncilMember.real_name'
        db.add_column(u'phillyleg_councilmember', 'real_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting model 'CouncilMemberAlias'
        db.delete_table(u'phillyleg_councilmemberalias')

        # Deleting field 'CouncilMember.real_name'
        db.delete_column(u'phillyleg_councilmember', 'real_name')

    models = {
        u'phillyleg.councildistrict': {
            'Meta': {'object_name': 'CouncilDistrict'},
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {}),
            'key': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'districts'", 'to': u"orm['phillyleg.CouncilDistrictPlan']"}),
            'shape': ('django.contrib.gis.db.models.fields.PolygonField', [], {}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'phillyleg.councildistrictplan': {
            'Meta': {'object_name': 'CouncilDistrictPlan'},
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'phillyleg.councilmember': {
            'Meta': {'object_name': 'CouncilMember'},
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'districts': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'representatives'", 'symmetrical': 'False', 'through': u"orm['phillyleg.CouncilMemberTenure']", 'to': u"orm['phillyleg.CouncilDistrict']"}),
            'headshot': ('django.db.models.fields.CharField', [], {'default': "'phillyleg/noun_project_416.png'", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'real_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'phillyleg.councilmembertenure': {
            'Meta': {'ordering': "('-begin',)", 'object_name': 'CouncilMemberTenure'},
            'at_large': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'begin': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            'councilmember': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tenures'", 'to': u"orm['phillyleg.CouncilMember']"}),
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tenures'", 'null': 'True', 'to': u"orm['phillyleg.CouncilDistrict']"}),
            'end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'president': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'phillyleg.legaction': {
            'Meta': {'ordering': "['date_taken']", 'unique_together': "(('file', 'date_taken', 'description', 'notes'),)", 'object_name': 'LegAction'},
            'acting_body': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_taken': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'file': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actions'", 'to': u"orm['phillyleg.LegFile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minutes': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actions'", 'null': 'True', 'to': u"orm['phillyleg.LegMinutes']"}),
            'motion': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'notes': ('django.db.models.fields.TextField', [], {}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'phillyleg.legfile': {
            'Meta': {'ordering': "['-key']", 'object_name': 'LegFile'},
            'contact': ('django.db.models.fields.CharField', [], {'default': "'No contact'", 'max_length': '1000'}),
            'controlling_body': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_scraped': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'final_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'intro_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'is_routine': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'key': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'last_scraped': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'sponsors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'legislation'", 'symmetrical': 'False', 'to': u"orm['phillyleg.CouncilMember']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'title': ('django.db.models.fields.TextField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'phillyleg.legfileattachment': {
            'Meta': {'unique_together': "(('file', 'url'),)", 'object_name': 'LegFileAttachment'},
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'file': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': u"orm['phillyleg.LegFile']"}),
            'fulltext': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'phillyleg.legfilemetadata': {
            'Meta': {'object_name': 'LegFileMetaData'},
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'legfile': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'metadata'", 'unique': 'True', 'to': u"orm['phillyleg.LegFile']"}),
            'locations': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'references_in_legislation'", 'symmetrical': 'False', 'to': u"orm['phillyleg.MetaData_Location']"}),
            'mentioned_legfiles': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'references_in_legislation'", 'symmetrical': 'False', 'to': u"orm['phillyleg.LegFile']"}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'references_in_legislation'", 'symmetrical': 'False', 'to': u"orm['phillyleg.MetaData_Topic']"}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'words': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'references_in_legislation'", 'symmetrical': 'False', 'to': u"orm['phillyleg.MetaData_Word']"})
        },
        u'phillyleg.councilmemberalias': {
            'Meta': {'object_name': 'CouncilMemberAlias'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'legislative_names'", 'to': u"orm['phillyleg.CouncilMember']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'phillyleg.legkeys': {
            'Meta': {'object_name': 'LegKeys'},
            'continuation_key': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'phillyleg.legminutes': {
            'Meta': {'object_name': 'LegMinutes'},
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_taken': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'fulltext': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'phillyleg.legminutesmetadata': {
            'Meta': {'object_name': 'LegMinutesMetaData'},
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'legminutes': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'metadata'", 'unique': 'True', 'to': u"orm['phillyleg.LegMinutes']"}),
            'locations': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'references_in_minutes'", 'symmetrical': 'False', 'to': u"orm['phillyleg.MetaData_Location']"}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'words': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'references_in_minutes'", 'symmetrical': 'False', 'to': u"orm['phillyleg.MetaData_Word']"})
        },
        u'phillyleg.legvote': {
            'Meta': {'object_name': 'LegVote'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': u"orm['phillyleg.LegAction']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'voter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': u"orm['phillyleg.CouncilMember']"})
        },
        u'phillyleg.metadata_location': {
            'Meta': {'object_name': 'MetaData_Location'},
            'address': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2048'}),
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'phillyleg.metadata_topic': {
            'Meta': {'object_name': 'MetaData_Topic'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'topic': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        u'phillyleg.metadata_word': {
            'Meta': {'object_name': 'MetaData_Word'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        }
    }

    complete_apps = ['phillyleg']