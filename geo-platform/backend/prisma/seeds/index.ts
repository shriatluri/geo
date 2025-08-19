import { config } from 'dotenv';
import { PrismaClient } from '@prisma/client';

// Load environment variables
config();

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Starting database seeding...');

  // Create a test user
  const testUser = await prisma.user.upsert({
    where: { email: 'test@geoplatform.com' },
    update: {},
    create: {
      email: 'test@geoplatform.com',
      name: 'Test User',
    },
  });

  console.log('✅ Created test user:', testUser.email);

  // Create a test site
  const testSite = await prisma.site.upsert({
    where: { domain: 'example.com' },
    update: {},
    create: {
      domain: 'example.com',
      name: 'Example Website',
      description: 'A test website for GEO analysis',
      userId: testUser.id,
    },
  });

  console.log('✅ Created test site:', testSite.domain);

  // Create a sample crawl job
  const crawlJob = await prisma.crawlJob.create({
    data: {
      siteId: testSite.id,
      status: 'COMPLETED',
      depth: 3,
      includeApis: true,
      startedAt: new Date(),
      completedAt: new Date(),
      progress: 100,
      totalPages: 10,
      crawlData: {
        pages: [
          {
            url: 'https://example.com',
            title: 'Example Domain',
            schemas: [
              {
                '@type': 'Organization',
                'name': 'Example Organization',
                'url': 'https://example.com'
              }
            ],
            apis: []
          }
        ],
        summary: {
          totalPages: 10,
          schemasFound: 1,
          apisFound: 0
        }
      }
    },
  });

  console.log('✅ Created test crawl job:', crawlJob.id);

  // Create a sample analysis
  const analysis = await prisma.analysis.create({
    data: {
      siteId: testSite.id,
      crawlJobId: crawlJob.id,
      status: 'COMPLETED',
      visibilityScore: 85,
      accuracyScore: 92,
      actionabilityScore: 78,
      overallScore: 85,
      startedAt: new Date(),
      completedAt: new Date(),
      analysisData: {
        visibility: {
          searchResults: 8,
          citationRate: 0.75,
          discoverability: 'good'
        },
        accuracy: {
          factualErrors: 0,
          inconsistencies: 1,
          reliability: 'high'
        },
        actionability: {
          apiEndpoints: 0,
          interactiveElements: 5,
          accessibility: 'good'
        }
      }
    },
  });

  console.log('✅ Created test analysis:', analysis.id);

  // Create sample recommendations
  await prisma.recommendation.createMany({
    data: [
      {
        analysisId: analysis.id,
        type: 'SCHEMA',
        priority: 'HIGH',
        title: 'Add Product Schema',
        description: 'Add structured data for better product visibility in AI searches',
        fixType: 'add_schema',
        implementation: {
          schemaType: 'Product',
          location: 'product pages',
          example: {
            '@type': 'Product',
            'name': 'Product Name',
            'description': 'Product description',
            'offers': {
              '@type': 'Offer',
              'price': '99.99',
              'priceCurrency': 'USD'
            }
          }
        },
        estimatedImpact: {
          visibility: 15,
          accuracy: 10,
          actionability: 5
        }
      },
      {
        analysisId: analysis.id,
        type: 'CONTENT',
        priority: 'MEDIUM',
        title: 'Add FAQ Section',
        description: 'Create comprehensive FAQ to improve AI understanding and user experience',
        fixType: 'update_content',
        implementation: {
          location: 'main pages',
          contentType: 'FAQ',
          suggestedQuestions: [
            'What services do you offer?',
            'How do I get started?',
            'What are your pricing options?'
          ]
        },
        estimatedImpact: {
          visibility: 10,
          accuracy: 15,
          actionability: 8
        }
      }
    ]
  });

  console.log('✅ Created test recommendations');

  console.log('🎉 Database seeding completed successfully!');
}

main()
  .catch((e) => {
    console.error('❌ Error during seeding:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
